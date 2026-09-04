"""The IRW format checks themselves, moved verbatim from
`automated_finding/irw_triage_updated.py::run_qc` (#1703 sub-item 1.3).

**Moved, not rewritten.** Fifty scripts in `data/` call `run_qc` and read
`c.name` / `c.status` / `c.detail` off what it returns, so the check bodies and
above all their *emission order* are preserved exactly. `irw_validate.compat`
re-exports this as `run_qc`, and `automated_finding/irw_triage_updated.py`
re-exports that, which is why none of the fifty needed an edit.

`irw_validate.core` layers severity profiles, extra checks and an exit code on
top of this; nothing here knows about any of that. The golden test in
`tests/test_validate.py` pins the (name, status) sequence for eight fixtures so
the move is provably behaviour-preserving.
"""
from __future__ import annotations

import collections
import re
from dataclasses import dataclass
from math import sqrt

import pandas as pd

#: Columns that say WHEN or UNDER WHAT a measurement was taken, per
#: `datastandard.md`. `group`, `study` and `treat` are deliberately absent: they
#: describe the person or the arm, so a person appearing twice under one is a
#: question, not an answer (#1835).
OCCASION = ("rt", "rater", "wave", "timepoint", "date", "trialnum", "trial",
            "order", "session", "occasion", "period", "block", "subtest")


@dataclass
class Check:
    name: str
    status: str    # "pass" | "warn" | "fail"
    detail: str


IRW_REQUIRED = ["id", "item", "resp"]
ITEM_LEVEL_PREFIXES = ("itemcov_", "qmatrix", "item_family", "rater")

_COMPOSITE_TOKENS = {
    "total", "totals", "composite", "subscale", "subscales", "overall",
    "average", "averages", "avg", "mean", "sum", "index", "score", "scores",
}
# Whole-label pre/post markers (optionally with a short subscale suffix, e.g.
# "pre-A", "post_F"). Matched only against the ENTIRE label: a genuine raw
# item at a pre-wave is usually "pre_anxiety_3", which must not trip this.
_PREPOST_LABEL = re.compile(
    r"^(pre|post|baseline|follow[-_ ]?up)[-_ ]?[a-z0-9]{0,2}$", re.I)

def _looks_composite(label) -> bool:
    """Does this item label name a computed score rather than a question?"""
    s = str(label).strip()
    if not s:
        return False
    if _PREPOST_LABEL.match(s):
        return True
    # Token-wise, so "meaning_1" doesn't match on "mean" and "scoreboard_2"
    # doesn't match on "score".
    tokens = {t.lower() for t in re.split(r"[^A-Za-z0-9]+", s) if t}
    return bool(tokens & _COMPOSITE_TOKENS)

def irw_metadata(df: pd.DataFrame) -> dict:
    """The IRW's own metadata/density computation, ported from their R/Python."""
    d = df.loc[~df["resp"].isna()].copy()
    d["resp"] = pd.to_numeric(d["resp"], errors="coerce")
    n_resp = len(d)
    n_part = d["id"].nunique()
    n_item = d["item"].nunique()
    # response frequency distribution — the professor's table(df$resp)
    resp_counts = d["resp"].value_counts().sort_index()
    resp_table = {str(k): int(v) for k, v in resp_counts.head(20).items()}
    return {
        "n_responses": n_resp,
        "n_categories": int(d["resp"].nunique()),
        "n_participants": n_part,
        "n_items": n_item,
        "responses_per_participant": round(n_resp / n_part, 2) if n_part else 0,
        "responses_per_item": round(n_resp / n_item, 2) if n_item else 0,
        "density": round((sqrt(n_resp) / n_part) * (sqrt(n_resp) / n_item), 4)
                   if n_part and n_item else 0,
        "resp_distribution": resp_table,
    }


def run_qc(df: pd.DataFrame, coercion_method: str = "",
           original_cols: list = None) -> list:
    """QC checks. The first block is ported directly from the IRW's official
    validate_irw.R (statuses: pass=OK, warn=NOTE, fail=ERROR). The second block
    is extra heuristics we add on top, clearly labelled."""
    checks = []
    original_cols = original_cols or []

    # ===== ported from validate_irw.R =====================================

    # required columns (ERROR if missing)
    missing = [c for c in IRW_REQUIRED if c not in df.columns]
    if missing:
        checks.append(Check("required_columns", "fail",
                            f"missing required columns: {', '.join(missing)}"))
        return checks  # nothing else is meaningful without these
    checks.append(Check("required_columns", "pass", "id/item/resp present"))

    # NAs in required columns: all-NA = ERROR, some-NA = NOTE
    for col in IRW_REQUIRED:
        n_na = df[col].isna().sum()
        if n_na == len(df):
            checks.append(Check(f"{col}_na", "fail", f"{col} is entirely NA"))
        elif n_na > 0:
            checks.append(Check(f"{col}_na", "warn", f"{col} has {n_na} NAs"))

    # resp must be numeric (ERROR)
    resp_num = pd.to_numeric(df["resp"], errors="coerce")
    if resp_num.notna().mean() < 0.99:
        checks.append(Check("resp_numeric", "fail",
                            f"resp is not numeric (only "
                            f"{resp_num.notna().mean():.0%} parse as numbers)"))
    else:
        checks.append(Check("resp_numeric", "pass", "resp is numeric"))

    # duplicate id+item: ERROR if no longitudinal column, else NOTE
    longitudinal = [c for c in ("wave", "timepoint", "date") if c in df.columns]
    dups = df.duplicated(subset=["id", "item"]).sum()
    if dups > 0 and not longitudinal:
        checks.append(Check("dup_id_item", "fail",
                            f"{dups} duplicate id+item rows with no "
                            "wave/timepoint/date column"))
    elif dups > 0:
        checks.append(Check("dup_id_item", "warn",
                            f"{dups} duplicate id+item rows "
                            f"(longitudinal column {longitudinal} present — likely ok)"))
    else:
        checks.append(Check("dup_id_item", "pass", "id+item rows unique"))

    # covariate naming: extra columns without a recognized name/prefix = NOTE.
    # (Broadened from validate_irw.R's narrow list to the full documented
    #  standard, so legitimate columns like item_family/treat aren't flagged.)
    #
    # OCCASION belongs in this set, and leaving it out made the validator
    # contradict itself: `dup_id_item` accepts `trialnum` as the column that
    # explains a repeat, and `cov_prefix` then told you to rename it `cov_`,
    # which would both misdescribe it -- a covariate is invariant to the person,
    # a trial index is the opposite -- and stop `dup_id_item` from seeing it,
    # re-breaking the table the rename had just fixed. Seen on `motion` and
    # `rr98_accuracy` (irw#1842 block J). One list, so the two cannot drift.
    known = {"id", "item", "resp", "date", "treat", "item_family"} | set(OCCASION)
    known_prefix = ("cov_", "itemcov_", "qmatrix", "trial_")
    unprefixed = [c for c in df.columns
                  if c not in known and not c.startswith(known_prefix)]
    if unprefixed:
        checks.append(Check("cov_prefix", "warn",
                            f"unrecognized columns (prefix with cov_ if "
                            f"covariates): {', '.join(unprefixed)}"))

    # ===== extra heuristics (beyond the official validator) ===============

    # resp scale sanity — flag a resp that looks continuous/mis-parsed
    ncat = resp_num.nunique()
    if ncat <= 1:
        checks.append(Check("resp_variation*", "fail",
                            "resp has no variation (1 unique value)"))
    elif ncat > 50:
        checks.append(Check("resp_ordinal*", "warn",
                            f"{ncat} distinct resp values — confirm continuous, "
                            "not mis-parsed"))

    # P1 #3: resp coding direction — can't auto-verify; always warn after melt.
    if coercion_method == "wide-to-long":
        checks.append(Check(
            "resp_direction*", "warn",
            "Cannot auto-verify: within each item, higher resp values must "
            "indicate more of the construct (IRW standard). Confirm no "
            "unreversed items."
        ))

    # P1 #4: imputed values — column name signals and mean-imputation signature.
    if original_cols:
        imputed_signals = [c for c in original_cols
                           if re.search(r"_imp(?:uted)?$|_filled$|_flag$", c,
                                        re.I)]
        if imputed_signals:
            checks.append(Check("imputed_values*", "warn",
                                f"Columns suggest imputed values may be present: "
                                f"{imputed_signals}. IRW requires their removal."))
    # Mean-imputation signature: any item where one value accounts for >60% of rows.
    if resp_num.notna().any():
        by_item = df.groupby("item")["resp"]
        for item_name, grp in by_item:
            vc = grp.value_counts(normalize=True)
            if not vc.empty and vc.iloc[0] > 0.60:
                checks.append(Check("imputed_values*", "warn",
                                    f"Item '{item_name}' has one resp value "
                                    f"accounting for {vc.iloc[0]:.0%} of responses "
                                    "— possible mean imputation."))
                break  # one warning is enough

    # P1 #5: date column validation.
    if "date" in df.columns:
        d = pd.to_numeric(df["date"], errors="coerce")
        if d.isna().mean() > 0.1:
            checks.append(Check("date_numeric*", "warn",
                                "date column is not numeric — IRW requires Unix "
                                "seconds (or seconds since first observation)"))
        elif d.notna().any() and d.max() < 1e8:
            checks.append(Check("date_range*", "warn",
                                f"date max={d.max():.0f} — looks too small for "
                                "Unix seconds; verify units"))

    # P1 #6: rt column validation.
    if "rt" in df.columns:
        rt = pd.to_numeric(df["rt"], errors="coerce")
        if rt.isna().mean() > 0.1:
            checks.append(Check("rt_numeric*", "warn",
                                "rt column is not numeric"))
        elif rt.notna().any():
            if rt.median() > 60000:
                checks.append(Check("rt_units*", "warn",
                                    f"rt median={rt.median():.0f} — likely "
                                    "milliseconds, not seconds (IRW requires "
                                    "seconds)"))
            if (rt < 0).any():
                checks.append(Check("rt_negative*", "warn",
                                    "rt has negative values"))

    # treat column should be 0/1 if present
    if "treat" in df.columns:
        bad = set(pd.unique(df["treat"].dropna())) - {0, 1}
        if bad:
            checks.append(Check("treat_binary*", "warn",
                                f"treat has non-0/1 values {sorted(bad)[:5]}"))

    # P2 #7: item-level columns dropped during melt — remind user to verify.
    if original_cols and coercion_method == "wide-to-long":
        item_level_found = [c for c in original_cols
                            if any(c.startswith(p) for p in ITEM_LEVEL_PREFIXES)]
        if item_level_found:
            checks.append(Check("item_level_cols*", "warn",
                                f"Item-level columns {item_level_found} were "
                                "excluded from the melt — verify they are "
                                "correctly aligned after conversion."))

    # P2 #7: multi-scale detection — distinct item-name prefixes suggest separate
    # constructs that must be split into separate tables.
    if "item" in df.columns:
        prefixes = [re.split(r"[\d_]", str(i))[0].lower()
                    for i in df["item"].unique() if str(i)]
        prefix_counts = pd.Series(prefixes).value_counts()
        dominant = prefix_counts[prefix_counts >= 3]
        if len(dominant) >= 2:
            checks.append(Check("multi_scale*", "warn",
                                f"Item names suggest {len(dominant)} subscales "
                                f"({list(dominant.index)[:4]}) — IRW requires "
                                "separate tables per construct."))

    # Response-scale homogeneity. The existing multi_scale* check reads item
    # *names*; this one reads the responses themselves, which is what actually
    # catches a mailing that bundled several instruments. Two distinct
    # failures fall out of the same per-item range profile:
    #   * a substantial minority of items on a different range  -> two scales
    #     in one table, which breaks "one table per construct" and leaves `resp`
    #     meaning different things in different rows;
    #   * one or two isolated items off the modal range -> almost always not
    #     an item at all (an administrative or count column swept in).
    # Both were live defects in the 2026-08-26 Eugene-Springfield build:
    # `sdv` spanned 1-5, 1-7, 1-8 and 1-9 at once, and `submiss` -- a
    # missing-response count, 94.8% zero -- was the only column in the HPQ
    # outside its 1-5 scale.
    if {"item", "resp"}.issubset(df.columns):
        rng = df.dropna(subset=["resp"]).groupby("item")["resp"].agg(["min", "max"])
        if len(rng) >= 3:
            profile = collections.Counter(zip(rng["min"], rng["max"]))
            (modal, modal_n), = profile.most_common(1)
            off = rng[(rng["min"] != modal[0]) | (rng["max"] != modal[1])]
            # Only a range that *exceeds* the modal one is evidence of a
            # different scale; an item nobody answered at the ceiling simply
            # has a lower observed max.
            over = off[(off["max"] > modal[1]) | (off["min"] < modal[0])]
            share = len(over) / len(rng)
            if share >= 0.15:
                other = collections.Counter(zip(over["min"], over["max"]))
                checks.append(Check("resp_scale_mixed", "fail",
                    f"items span more than one response scale: "
                    f"{modal_n} on {modal[0]}-{modal[1]} and {len(over)} on "
                    f"{[f'{a}-{b}' for a, b in list(other)[:3]]}. IRW requires "
                    "one table per construct; split before submitting."))
            elif len(over):
                checks.append(Check("item_scale_outlier", "warn",
                    f"{len(over)} item(s) fall outside the table's "
                    f"{modal[0]}-{modal[1]} scale: {list(over.index)[:4]}. An "
                    "isolated out-of-range column is usually not an item -- "
                    "check for an administrative or count field."))

    # Composite columns masquerading as items. A summary table melts into a
    # perfectly well-formed id/item/resp frame and passes every structural
    # check above -- the only tell is what the items are NAMED.
    if "item" in df.columns:
        labels = [i for i in df["item"].unique() if str(i).strip()]
        comp = [i for i in labels if _looks_composite(i)]
        if labels and len(comp) == len(labels):
            checks.append(Check("composite_items*", "fail",
                                f"every item label names a computed score "
                                f"({[str(c) for c in comp[:4]]}) — this looks "
                                "like a summary/aggregate table, not raw "
                                "item-level responses"))
        elif comp:
            checks.append(Check("composite_items*", "warn",
                                f"{len(comp)}/{len(labels)} item labels name "
                                f"computed scores ({[str(c) for c in comp[:4]]}) "
                                "— drop them, or confirm they are real items"))

    # IRW's own density signal — very sparse data is worth a look
    meta = irw_metadata(df)
    if meta["density"] < 0.01:
        checks.append(Check("density*", "warn",
                            f"very sparse (density={meta['density']}); fine for "
                            "adaptive/booklet designs, else verify"))

    return checks
