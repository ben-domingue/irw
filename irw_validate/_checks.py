"""The IRW format checks themselves, moved verbatim from
`automated_finding/irw_triage_updated.py::run_qc` (#1703 sub-item 1.3).

Fifty scripts in `data/` call `run_qc` and read
`c.name` / `c.status` / `c.detail` off what it returns. `irw_validate.compat`
re-exports this as `run_qc`, and `automated_finding/irw_triage_updated.py`
re-exports that, which is why none of the fifty needed an edit.

`irw_validate.core` layers severity profiles, extra checks and an exit code on
top of this; nothing here knows about any of that. The golden test in
`tests/test_validate.py` pins the reviewed (name, status) sequence for eight
fixtures. PR #1697 deliberately revises the
response-range checks: observed ranges alone warn; they do not identify constructs.
"""
from __future__ import annotations

import collections
import re
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from math import isfinite, sqrt
from numbers import Integral

import numpy as np
import pandas as pd

#: Columns that say WHEN or UNDER WHAT a measurement was taken, per
#: `datastandard.md`. `group`, `study` and `treat` are deliberately absent: they
#: describe the person or the arm, so a person appearing twice under one is a
#: question, not an answer (#1835).
OCCASION = ("rt", "rater", "wave", "timepoint", "date", "trialnum", "trial",
            "order", "session", "occasion", "period", "block", "subtest")


def occasion_columns(df) -> list:
    """Occasion columns present that may legitimately key a repeated id+item.

    `rt` is in OCCASION for naming purposes but is excluded here: it is a
    measurement, and rounding it would silently merge rows (#1842 blocks I
    and J). `trial_*` columns count -- the published trial tables index their
    trials as `trial_number`, `trial_num`, `trial_index` or `trial_block`.

    Hoisted out of core.py so `dup_id_item`'s message and the gate's rescue
    cannot disagree about which keys were considered (#2314).
    """
    cols = [c for c in OCCASION if c != "rt" and c in df.columns]
    cols += [c for c in df.columns
             if str(c).startswith("trial_") and c not in cols]
    return cols


def resolve_occasion(df, cols):
    """Which occasion key makes id+item unique, and what survives if none does.

    Returns ``(resolved_by, residual)``. Keys are tested individually in `cols`
    order, then all of them together -- a design can be keyed by more than one
    at once (`rr98_accuracy` restarts its trial index inside each block, so
    neither column identifies a row alone and both together identify it
    exactly). `residual` is the excess-row count under the full combination:
    what a reader would still have to explain, which is the number the old
    "likely ok" wording asserted away without measuring (#2314).
    """
    for col in cols:
        if not df.duplicated(subset=["id", "item", col]).any():
            return col, 0
    if len(cols) > 1 and not df.duplicated(subset=["id", "item"] + cols).any():
        return "+".join(cols), 0
    residual = int(df.duplicated(subset=["id", "item"] + cols).sum())
    return None, residual


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


def _as_value_set(raw):
    """A codebook collection, never a set inferred from observed responses."""
    if isinstance(raw, (str, bytes, Mapping)) or raw is None:
        return None, "expected a non-empty collection of numeric values"
    try:
        values = list(raw)
    except TypeError:
        return None, "expected a collection of numeric values"
    if not values:
        return None, "permitted-value collection is empty"
    result = set()
    for value in values:
        try:
            # Preserve exact integer codes, including numeric strings above
            # float64's consecutive-integer limit. Keep decimal fractions exact
            # until the response dtype is known; do not round them into integers.
            if isinstance(value, Integral):
                number = int(value)
            elif isinstance(value, (str, Decimal)):
                parsed = Decimal(value)
                if not parsed.is_finite():
                    return None, f"{value!r} is not finite"
                number = int(parsed) if parsed == parsed.to_integral_value() else parsed
            else:
                number = float(value)
        except (TypeError, ValueError, OverflowError, InvalidOperation):
            return None, f"{value!r} is not numeric"
        if not isinstance(number, (int, Decimal)) and not isfinite(number):
            return None, f"{value!r} is not finite"
        result.add(number)
    return frozenset(result), None


def _at_response_precision(values, dtype):
    """Compare fractional codes in the stored float dtype, without tolerance.

    For example, a float32 response 0.1 and a documented Python float 0.1
    encode the same category despite different binary representations. Exact
    integer codes are never rounded into adjacent categories by this step.
    """
    if not pd.api.types.is_float_dtype(dtype):
        return values
    dtype = getattr(dtype, "numpy_dtype", dtype)
    result = set()
    with np.errstate(over="ignore"):
        for value in values:
            fractional_float = (isinstance(value, float) and
                                not value.is_integer() and dtype.itemsize < 8)
            if isinstance(value, Decimal) or fractional_float:
                represented = float(dtype.type(value))
                result.add(represented if isfinite(represented) else value)
            else:
                result.add(value)
    return result


def _permitted_by_item(items, permitted_values):
    """Return known sets, full coverage, and reasons for unusable entries.

    An incomplete codebook cannot clear a warning, but a valid entry in it
    can still expose a violation. Item keys are matched exactly, not coerced.
    """
    if permitted_values is None:
        return {}, False, []
    if not items:
        return {}, False, ["table has no non-missing item labels"]
    if not isinstance(permitted_values, Mapping):
        shared, why = _as_value_set(permitted_values)
        if why:
            return {}, False, [why]
        return {item: shared for item in items}, True, []
    known, reasons = {}, []
    for item in items:
        if item not in permitted_values:
            reasons.append(f"item {item!r}: no permitted values supplied")
            continue
        allowed, why = _as_value_set(permitted_values[item])
        if why:
            reasons.append(f"item {item!r}: {why}")
        else:
            known[item] = allowed
    return known, not reasons, reasons


def _constructs_by_item(items, item_constructs):
    """Only explicit source-supported construct labels can upgrade a finding.

    Names such as MC/CR and disjoint respondent sets can describe one test's
    design. Neither is converted into construct membership here.
    """
    if item_constructs is None:
        return {}, False, []
    if not isinstance(item_constructs, Mapping):
        return {}, False, ["expected a mapping from item labels to documented constructs"]
    if not items:
        return {}, False, ["table has no non-missing item labels"]
    known, reasons = {}, []
    for item in items:
        label = item_constructs.get(item)
        if not isinstance(label, str) or not label.strip():
            reasons.append(f"item {item!r}: missing or blank construct label")
        else:
            known[item] = label.strip()
    return known, not reasons, reasons


def _response_scale_checks(df, resp_num, permitted_values, item_constructs):
    checks = []
    items = list(pd.unique(df["item"].dropna()))
    observed = df.assign(_resp_num=resp_num).dropna(subset=["item", "_resp_num"])
    allowed, complete, reasons = _permitted_by_item(items, permitted_values)
    if reasons:
        checks.append(Check("permitted_values_unusable", "warn",
            "Cannot use the supplied permitted values for every item: "
            + "; ".join(reasons[:3])
            + ". Valid entries are still checked; missing categories are not inferred."))
    violations = {}
    if allowed:
        for item, group in observed.groupby("item", observed=True):
            if item not in allowed:
                continue
            permitted = _at_response_precision(allowed[item], resp_num.dtype)
            bad = sorted(set(group["_resp_num"]) - permitted)
            if bad:
                violations[item] = bad
    if violations:
        checks.append(Check("resp_outside_permitted", "fail",
            f"{len(violations)} item(s) contain responses outside their documented "
            "permitted values: "
            + "; ".join(f"{item!r}: {[str(v) for v in values[:4]]}"
                        for item, values in list(violations.items())[:3])
            + ". Check the source codebook and conversion; do not silently recode or drop responses."))

    constructs, constructs_complete, reasons = _constructs_by_item(items, item_constructs)
    if reasons:
        checks.append(Check("item_constructs_unusable", "warn",
            "Cannot use the supplied construct mapping: " + "; ".join(reasons[:3])
            + ". Partial or inferred membership cannot establish a construct boundary."))
    ranges = observed.groupby("item", observed=True)["_resp_num"].agg(["min", "max"])

    # This evidence path is independent of codebook validity and sample size.
    # Different legitimate item scoring sets do not prove a single construct.
    if constructs_complete and not ranges.empty:
        grouped = ranges.assign(_construct=[constructs[item] for item in ranges.index])
        bounds = grouped.groupby("_construct").agg(lo=("min", "min"), hi=("max", "max"))
        if len(bounds) > 1 and len(set(zip(bounds["lo"], bounds["hi"]))) > 1:
            detail = "; ".join(f"{name!r}: {row.lo:g}-{row.hi:g}"
                               for name, row in bounds.head(4).iterrows())
            checks.append(Check("resp_scale_constructs", "fail",
                "Different observed response ranges align with explicitly supplied "
                f"documented constructs ({detail}). Review the source-supported "
                "construct boundaries and separate distinct constructs as required; "
                "this finding is not inferred from item prefixes or response width alone."))
            return checks

    # A complete codebook validates each item's scores, including different
    # legitimate sets on weighted or mixed-format tests. It says nothing about
    # the construct identity of undocumented items or upstream preprocessing.
    # Keep the upstream #2029 guard: mixed numeric/text responses do not
    # support a width heuristic. Documented numeric violations above remain
    # reportable; the numeric check reports the invalid tokens separately.
    mixed_numeric_text = (resp_num.notna().any()
                          and (df["resp"].notna() & resp_num.isna()).any())
    if mixed_numeric_text or len(ranges) < 3 or (complete and not violations):
        return checks
    profiles = collections.Counter(zip(ranges["min"], ranges["max"]))
    if len(profiles) < 2:
        return checks

    # Use a deterministic tie break and all deviations, not only deviations
    # above the modal maximum. Which item format is in the majority cannot
    # decide whether a mixed-format test is valid.
    modal = min(profiles, key=lambda bounds: (-profiles[bounds], bounds))
    off = ranges[(ranges["min"] != modal[0]) | (ranges["max"] != modal[1])]
    ordered = sorted(profiles, key=lambda bounds: (bounds[0], -bounds[1]))
    nested = all(a[1] >= b[1] for a, b in zip(ordered, ordered[1:]))
    # An isolated wider column can contain the modal interval (e.g. HPQ's
    # missing-response count). Keep that targeted diagnostic before nesting;
    # rarity alone still cannot establish that the column is invalid.
    if len(off) / len(ranges) < 0.15:
        name = "item_scale_outlier"
        examples = ", ".join(f"{item!r} ({row['min']:g}-{row['max']:g})"
                             for item, row in off.head(4).iterrows())
        reason = (f"{len(off)} item(s) differ from the modal observed range "
                  f"{modal[0]:g}-{modal[1]:g}: {examples}")
    elif nested:
        name = "resp_scale_nested_support"
        reason = "Item observed min/max ranges are nested"
    else:
        name = "resp_scale_mixed"
        reason = "Items have non-nested observed response ranges"
    summary = ", ".join(f"{lo:g}-{hi:g} ({profiles[(lo, hi)]} items)"
                        for lo, hi in sorted(profiles)[:4])
    checks.append(Check(name, "warn",
        f"{reason}: {summary}. Observed ranges do not establish permitted values "
        "or separate constructs. Category non-use, item weights and mixed item "
        "formats can be legitimate. Review source documentation; do not split "
        "a single construct solely because its item ranges differ."))
    return checks


def run_qc(df: pd.DataFrame, coercion_method: str = "",
           original_cols: list = None, permitted_values=None,
           item_constructs=None, profile: str = "") -> list:
    """QC checks. The first block is ported directly from the IRW's official
    validate_irw.R (statuses: pass=OK, warn=NOTE, fail=ERROR). The second block
    is extra heuristics we add on top, clearly labelled.

    Optional permitted_values is an external codebook collection shared by
    all items, or an item-keyed mapping of collections. Optional item_constructs
    maps every item to a source-supported construct label. Neither is inferred
    from observed scores, item names, or respondent overlap. See README.md.
    """
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

    # NAs in required columns: all-NA = ERROR, some-NA = NOTE.
    #
    # Whether a literal "NA"-style token counts as missing depends on who read
    # the file. validate_file() keeps such tokens as text for the gate profiles
    # (#2029); triage and the data/ callers let the reader parse them as
    # missing. So the same table yields different counts here, and the message
    # must not claim more than the profile can support. 22 finding/column pairs
    # in the #1728 sample had zero source typed nulls and tokens parsed as
    # missing, which the old bare "N NAs" reported as if they were the same
    # thing (#2314 item 4).
    if profile in ("upload", "legacy"):
        na_note = ("Literal 'NA'-style text is read as a response on this "
                   "profile, not as missing, so these are empty cells in the "
                   "frame as read.")
    else:
        na_note = ("These may be empty cells or literal 'NA'-style text the "
                   "reader parsed as missing; the two are not distinguished "
                   "here.")
    for col in IRW_REQUIRED:
        n_na = df[col].isna().sum()
        if n_na == len(df):
            checks.append(Check(f"{col}_na", "fail",
                                f"{col} has no usable values: all {len(df)} "
                                f"row(s) are missing. {na_note}"))
        elif n_na > 0:
            checks.append(Check(f"{col}_na", "warn",
                                f"{col} has {n_na} missing value(s). "
                                f"{na_note}"))

    # Judge numeric parsing only among present responses. Missingness belongs
    # to resp_na above, not to the nonnumeric count (#2314 item 2). Preserve
    # the raw/triage 99% threshold; upload/legacy separately require every
    # present value to parse in core.py.
    resp_num = pd.to_numeric(df["resp"], errors="coerce")
    present = df["resp"].notna()
    n_present = int(present.sum())
    n_numeric = int(resp_num[present].notna().sum())
    if not n_present:
        checks.append(Check("resp_numeric", "pass",
                            "No non-missing resp values to check; "
                            "missingness is reported by resp_na"))
    elif n_numeric / n_present < 0.99:
        checks.append(Check("resp_numeric", "fail",
                            f"resp is not numeric (only "
                            f"{n_numeric}/{n_present} non-missing responses "
                            f"parse as numbers, {n_numeric / n_present:.0%})"))
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
        # The old wording said "likely ok" on the mere PRESENCE of a wave /
        # timepoint / date column, without testing whether it explains anything.
        # 14 of 15 sampled reassurances were wrong: the repeats survived every
        # accepted occasion key and their full combination, F185 retaining 4,552
        # excess key rows after `wave` and `trial_number` (#2314 item 3). Report
        # what was tested and what is left instead of reassuring.
        occ = occasion_columns(df)
        resolved_by, residual = resolve_occasion(df, occ)
        tested = ", ".join(occ) if occ else "none"
        if resolved_by is not None:
            detail = (f"{dups} duplicate id+item rows, made unique by "
                      f"{resolved_by} (occasion columns tested: {tested})")
        else:
            detail = (f"{dups} duplicate id+item rows; {residual} excess row(s) "
                      f"remain after keying on every occasion column present, "
                      f"individually and combined (tested: {tested})")
        checks.append(Check("dup_id_item", "warn", detail))
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
    # `resp_raw` is in datastandard.md's schema table and the standard goes out
    # of its way to insist on that spelling over `raw_resp` -- but it was absent
    # here, so the validator warned about the one spelling it asks for. Seen on
    # `fitz_2024_numeracy`, whose free-text numeracy answers need it.
    known = {"id", "item", "resp", "resp_raw", "date", "treat",
             "item_family"} | set(OCCASION)
    known_prefix = ("cov_", "itemcov_", "qmatrix", "trial_")
    unprefixed = [c for c in df.columns
                  if c not in known and not c.startswith(known_prefix)]
    if unprefixed:
        checks.append(Check("cov_prefix", "warn",
                            f"unrecognized columns (prefix with cov_ if "
                            f"covariates): {', '.join(unprefixed)}"))

    # ===== extra heuristics (beyond the official validator) ===============

    # resp scale sanity — flag a resp that looks continuous/mis-parsed
    # `ncat` counts NUMERIC categories: text becomes NaN under the coercion
    # above and drops out. So stored text gives zero categories, not one, and
    # saying "1 unique value" of a column holding five distinct labels was
    # simply false (#2314 item 6). The numeric-response requirement is
    # unchanged -- both cases still fail, and resp_variation* is still a
    # GATE_ERROR -- but the two are no longer described as the same thing.
    ncat = resp_num.nunique()
    if ncat == 0:
        stored = df["resp"].dropna().nunique()
        if stored == 0:
            detail = "resp has no values at all"
        else:
            detail = (f"resp has no numeric values: {stored} distinct value(s) "
                      "are stored as text. IRW requires numeric responses. This "
                      "is zero numeric categories, not one response value.")
        checks.append(Check("resp_variation*", "fail", detail))
    elif ncat == 1:
        checks.append(Check("resp_variation*", "fail",
                            "resp has no variation (1 unique numeric value)"))
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
    # Response concentration: any item where one value accounts for >60% of rows.
    #
    # This used to be reported as "possible mean imputation". It was 52% of all
    # alert volume in the #1728 triage pass and 0 of 30 sampled messages were
    # supported -- all 30 came back cannot-tell, because a table cannot
    # establish WHY it looks the way it does. Valid binary or ordered-category
    # data exceeds a 60% modal share routinely. So the check keeps its
    # observation and drops its causal claim (#2314 item 1).
    #
    # It also used to break after the first hit and then name that one item, so
    # the message read as though it were the only concentrated item. Count them
    # all and say so.
    if resp_num.notna().any():
        concentrated = []
        for item_name, grp in df.groupby("item")["resp"]:
            vc = grp.value_counts(normalize=True)
            if not vc.empty and vc.iloc[0] > 0.60:
                concentrated.append((item_name, float(vc.iloc[0])))
        if concentrated:
            worst_item, worst_share = max(concentrated, key=lambda t: t[1])
            n_items = df["item"].nunique()
            checks.append(Check(
                "imputed_values*", "warn",
                f"{len(concentrated)} of {n_items} item(s) have a single resp "
                f"value covering over 60% of their responses (highest: "
                f"'{worst_item}' at {worst_share:.0%}). This reports response "
                "concentration only and does not establish a cause: binary and "
                "ordered-category items reach these shares legitimately. Check "
                "the source if you need to know whether values were imputed."))

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

    # P1 #6: rt column validation. The standard reads `rt` as the seconds one
    # item response took, so the checks here test that sentence from three
    # sides: the units, the values, and whether the column is item-level at
    # all. The old units threshold (median > 60000) only caught a table whose
    # median item took over 16 hours of seconds; a source recording
    # milliseconds usually lands far below that and passed silently.
    if "rt" in df.columns:
        rt = pd.to_numeric(df["rt"], errors="coerce")
        if rt.isna().mean() > 0.1:
            checks.append(Check("rt_numeric*", "warn",
                                "rt column is not numeric"))
        elif rt.notna().any():
            med = float(rt.median())
            if med > 1000:
                checks.append(Check("rt_units*", "warn",
                                    f"rt median={med:.0f} — read as seconds "
                                    f"that is {med / 60:.0f} minutes for a "
                                    "single item response. If the source "
                                    "recorded milliseconds, divide by 1000; "
                                    "IRW requires seconds. If the time really "
                                    "is that long, say so in the processing "
                                    "notes."))
            if (rt < 0).any():
                checks.append(Check("rt_negative*", "warn",
                                    "rt has negative values"))
            zero_share = float((rt == 0).mean())
            if zero_share > 0.01:
                checks.append(Check("rt_zero*", "warn",
                                    f"{zero_share:.0%} of rt values are "
                                    "exactly 0. No response takes no time, so "
                                    "these are a sentinel (missing, timed out, "
                                    "carried over) rather than a measurement — "
                                    "verify against the source and blank them "
                                    "if they are not times."))
            # An `rt` that never varies across the items answered at one
            # occasion is not the time that item took: it is the duration of
            # the whole beep/survey/block, copied onto every row. Only occasion
            # keys other than rt can define "one sitting" (`occasion_columns`
            # excludes rt for the same reason).
            keys = [c for c in occasion_columns(df) if c in df.columns]
            if keys and "id" in df.columns and "item" in df.columns:
                sub = df.loc[rt.notna(), ["id", "item"] + keys].copy()
                sub["__rt"] = rt[rt.notna()]
                grp = sub.groupby(["id"] + keys, observed=True)
                n_items = grp["item"].nunique()
                multi = n_items[n_items > 1].index
                if len(multi) >= 20:
                    constant = grp["__rt"].nunique().loc[multi].eq(1)
                    share = float(constant.mean())
                    if share > 0.9:
                        checks.append(Check("rt_item_level*", "warn",
                                            f"rt is identical across the items "
                                            f"answered at the same occasion in "
                                            f"{share:.0%} of {len(multi)} "
                                            f"person-occasions (keyed by "
                                            f"{keys}). That is an occasion-level "
                                            "duration or latency, not the "
                                            "per-item response time `rt` means "
                                            "in the standard — rename it to a "
                                            "`cov_` column or document it."))

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

    # Prefixes are a review hint: MC/CR can be two formats of one construct.
    if "item" in df.columns:
        # Trim first: F246 carries both `question ` (21 labels) and `question`
        # (14), which are one 35-label group and were counted as two (#2314
        # item 7). Whitespace only -- the source item IDs are never rewritten,
        # and the normalized prefix is deliberately not reported as a construct.
        prefixes = [re.split(r"[\d_]", str(i).strip())[0].strip().lower()
                    for i in df["item"].unique() if str(i)]
        prefix_counts = pd.Series(prefixes).value_counts()
        dominant = prefix_counts[prefix_counts >= 3]
        if len(dominant) >= 2:
            checks.append(Check("multi_scale*", "warn",
                                f"Item names have {len(dominant)} repeated prefixes "
                                f"({list(dominant.index)[:4]}). Verify whether they "
                                "denote constructs, item formats or design blocks "
                                "before considering separate tables."))

    checks.extend(_response_scale_checks(df, resp_num, permitted_values, item_constructs))

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
