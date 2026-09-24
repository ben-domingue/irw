"""The public API: validate a frame or a file, get a Report with an exit code."""
from __future__ import annotations

import os
from pathlib import Path

from . import extra
from ._checks import (irw_metadata, occasion_columns,
                      resolve_occasion, run_qc)
from .model import STANDARD_VERSION, Finding, Report, severity_for

#: Above this, a full pandas load is not worth it inside the uploader's hot
#: path -- red_up streams 500 MB tables with the csv module on purpose. Files
#: over the cap get a core-only streaming pass and an explicit `info` finding
#: recording the downgrade, so a skipped check is never silent.
MAX_BYTES = 512 * 1024 ** 2


#: Every extension a table can arrive as. Matched case-insensitively: the legacy
#: files are `.Rdata`, and stripping only `.csv` made every one of the 922 fail
#: the lowercase-name rule on the capital R of its own extension.
TABLE_SUFFIXES = (".csv", ".tsv", ".txt", ".rdata", ".rda", ".rds")


def _pipeline_root():
    """The `irw` checkout this package sits inside, or None if there is none.

    `irw_validate` is installable on its own (`pip install irw-validate`), and
    a contributor who does that has the validator but not the pipeline around
    it. Two loaders below need that pipeline; everything else -- every CSV, and
    `validate_frame` on a frame the caller already has -- needs pandas and
    nothing more. Checking rather than assuming turns an ImportError raised
    from three frames down into a sentence saying what to do.
    """
    root = Path(__file__).resolve().parent.parent
    return root if (root / "automated_finding" / "irw_triage_updated.py").is_file() else None


def _table_name(label: str) -> str:
    stem = Path(label).name
    low = stem.lower()
    for suffix in TABLE_SUFFIXES:
        if low.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


#: Item text tables have their own schema (`table`/`item`/`item_text`), and the
#: response-data checks are meaningless against them -- `id` does not exist,
#: `resp` is an option key rather than an answer, and one row per option is not
#: a duplicate. red_up already routes on this suffix; so does this.
ITEMS_SUFFIX = "__items"
ITEMS_REQUIRED = ("table", "item", "item_text")


def is_item_text(label: str) -> bool:
    return _table_name(label).endswith(ITEMS_SUFFIX)


def _addressable_key(df):
    """The (item, address) key an option row is joined on, per #1945/#2185.

    Returns the key frame and a short name for the address column, so a finding
    can say which column actually collided. `resp` is the address where it is
    populated; `raw_resp` is the fallback the schema provides for sources that
    print options with no scoring key. Returns (None, "resp") when there is no
    `item` column to key on at all.
    """
    if "item" not in df.columns:
        return None, "resp"
    if "resp" not in df.columns:
        if "raw_resp" in df.columns:
            return df[["item", "raw_resp"]].copy(), "raw_resp"
        return df[["item"]].copy(), "resp"
    if "raw_resp" not in df.columns:
        return df[["item", "resp"]].copy(), "resp"
    key = df[["item"]].copy()
    key["addr"] = df["resp"].where(df["resp"].notna(), df["raw_resp"])
    return key, "resp-or-raw_resp"


def _validate_item_text(df, label: str, profile: str) -> Report:
    """The item text schema: check what applies, and say nothing about the rest."""
    report = Report(label=label, profile=profile, kind="item_text")
    table = _table_name(label)[: -len(ITEMS_SUFFIX)]
    missing = [c for c in ITEMS_REQUIRED if c not in df.columns]
    report.checks_run.append("required_columns")
    if missing:
        report.findings.append(Finding(
            "required_columns", "error",
            f"missing required columns for item text: {', '.join(missing)}",
            table=table, group="core"))
        return report
    # THE KEY IS THE ADDRESSABLE ONE, NOT `resp` (#2232).
    #
    # The settled rule (#1945/#2185) is that an option row must be addressable:
    # it carries `resp`, or -- where the source prints bare options with no
    # scoring key -- `raw_resp`. Keying on `resp` alone broke that in two
    # directions at once, because two pandas calls disagree about what a null
    # key means. `duplicated()` treats NaN as equal to NaN, so with `resp`
    # blank every option row of an item collided; `groupby` DROPS NaN keys by
    # default, so the frame that would have told the two faults apart came back
    # empty and the run fell through to a message asserting the option text was
    # identical when it was the only thing distinguishing the rows. On
    # gilbert_meta_70 those rows read "gaadee", "kauaa", "kainchee" -- three
    # different words a child was asked to name.
    #
    # So both calls key on `resp` where it is populated and `raw_resp` where it
    # is not. A row with NEITHER populated has no address at all, still
    # collides, and is still reported -- that is the defect this check exists
    # for, and it is the case the previous fix attempt lost by dropping unkeyed
    # rows instead of falling back.
    report.checks_run.append("dup_item_resp")
    key_cols, addr_desc = _addressable_key(df)
    dup = int(key_cols.duplicated().sum()) if key_cols is not None else 0

    # A scored table is a different object. Where `correct_response` is
    # populated, `resp` is a scoring key (0 wrong / 1 right) rather than a point
    # on a scale, so one resp value legitimately carries many option labels --
    # spanishmegastudy has 1,270 multiple-choice items with three distractors
    # each, all coded resp=0. Judging that by the Likert rule would flag 1,270
    # correct items. For a scored table the only thing that still holds is that
    # no *whole row* should repeat.
    scored = False
    if "correct_response" in df.columns:
        col = df["correct_response"]
        # notna() first: under pandas 3 an all-NaN column astype(str) keeps the
        # values MISSING rather than rendering them "nan", so a string-only test
        # matches nothing and reads an empty column as fully populated.
        filled = col.notna() & ~col.astype(str).str.strip().isin(("", "NA", "nan", "None"))
        scored = bool(filled.mean() > 0.5)
    # AN EXACT WHOLE-ROW REPEAT IS A DOUBLED UPLOAD WHATEVER THE SHAPE (#2232),
    # so it is checked before the scored/unscored split rather than inside the
    # scored branch. It was only ever reached for scored tables, which meant an
    # unscored table's doubled upload was reported as `dup_item_resp` -- true,
    # but the vaguer of the two: `dup_item_resp` says a key repeats, `dup_row`
    # says the file contains the same row twice, which names the fault.
    #
    # NOTHING NEWLY FAILS. An exact whole-row duplicate is a strict subset of a
    # duplicate (item, addressable key) carrying identical option_text, so any
    # table this now catches was already failing on `dup_item_resp`. What
    # changes is which finding it gets, and that only for unscored tables.
    report.checks_run.append("dup_row")
    exact = int(df.duplicated().sum())
    if exact:
        report.findings.append(Finding(
            "dup_row", "error",
            f"{exact} fully identical row(s) -- an item text table carries one row "
            f"per response option, so a repeat is a doubled upload (#1810). On a "
            f"scored table `resp` is a key and one value carrying several option "
            f"labels is expected, but an exact repeat is a duplicate either way.",
            table=table, group="core"))
    elif scored:
        pass                          # handled above; resp is a key here
    elif dup:
        # Two different faults produce this, and the distinction matters to
        # whoever has to fix it, so name which one this is. If the repeated rows
        # carry the SAME option_text it is a doubled upload (#1810/#1816). If
        # they carry DIFFERENT option_text, the table is asserting that one
        # response value means two things -- afps_vangsness_2019 maps resp=1 to
        # both "Strongly agree" and "Strongly disagree", which is two opposite
        # scale directions written into one table and is worse than a duplicate.
        conflicting = 0
        if "option_text" in df.columns and key_cols is not None:
            # dropna=False on the GROUPBY as well. The parameter of the same
            # name on nunique() governs the values; this one governs the keys,
            # and without it a row with no addressable key vanishes from the
            # comparison rather than being judged by it.
            per_key = df.groupby([key_cols[c] for c in key_cols.columns],
                                 dropna=False)["option_text"].nunique(dropna=False)
            conflicting = int((per_key > 1).sum())
        if conflicting:
            report.findings.append(Finding(
                "resp_ambiguous", "error",
                f"{conflicting} response value(s) carry more than one option label -- "
                f"the same item+{addr_desc} is documented as meaning two different things, so "
                f"nothing joining item text to responses can resolve it. Usually two "
                f"opposite scale directions merged into one table.",
                table=table, group="core"))
        else:
            report.findings.append(Finding(
                "dup_item_resp", "error",
                f"{dup} duplicate item+{addr_desc} rows with identical option text -- "
                f"an item text table carries one row per response option, so a repeat "
                f"is a doubled upload (#1810). Rows carrying neither `resp` nor "
                f"`raw_resp` have no addressable key and count here: nothing can join "
                f"them to a response (#2232)",
                table=table, group="core"))
    for finding in extra.check_name(table):
        report.checks_run.append(finding.check)
        report.findings.append(finding)
    report.stats = {"n_rows": len(df),
                    "n_items": int(df["item"].nunique()) if "item" in df else 0}
    return report


def validate_frame(df, *, label: str = "", profile: str = "upload",
                   context: dict | None = None) -> Report:
    """Run every check the profile asks for against an in-memory frame.

    context may supply external codebook ``permitted_values`` and documented
    ``item_constructs`` mappings; see irw_validate/README.md for their contract.
    """
    context = context or {}
    if is_item_text(label):
        return _validate_item_text(df, label, profile)
    report = Report(label=label, profile=profile)
    table = _table_name(label)

    for check in run_qc(df,
                        coercion_method=context.get("coercion_method", ""),
                        original_cols=context.get("original_cols"),
                        permitted_values=context.get("permitted_values"),
                        item_constructs=context.get("item_constructs"),
                        profile=profile):
        report.checks_run.append(check.name)
        severity = severity_for(check.name, check.status, profile)
        if severity is None:
            continue
        group = "core" if check.name in ("required_columns", "cov_prefix") \
            or check.name.endswith("_na") or check.name in ("resp_numeric", "dup_id_item") \
            else "heuristic"
        report.findings.append(
            Finding(check.name, severity, check.detail, table=table, group=group))

    # `dup_id_item` asks whether a `wave`/`timepoint`/`date` column explains a
    # repeated id+item. That list came from validate_irw.R and is stale: it
    # predates `rater`, and it never covered trial-level designs. In the legacy
    # sweep it flagged 101 tables, and of the 57 whose local copy matches what is
    # published, 14 are explained outright by a column the check does not look
    # at -- `rater` on eleven of them, plus `trialnum`, `order` and `period`.
    #
    # A rater is not a defect: two people rating the same person on the same item
    # is the design. Same for a repeated trial. `datastandard.md` documents
    # `rater` as a legitimate column, so a check that treats it as a duplicate is
    # reporting the standard's own schema as an error.
    #
    # NOT included: `group`, `study`, `treatment`. Those describe the person or
    # the arm, not the occasion, and a person appearing twice under them is a
    # real question rather than an explanation.
    if profile in ("upload", "legacy") and {"id", "item"}.issubset(df.columns):
        # Which columns count, and why `rt` does not, is documented on
        # occasion_columns() in _checks.py. Both live there rather than here so
        # that this rescue and `dup_id_item`'s own message test the same keys
        # and cannot drift (#2314). resolve_occasion() tries each column alone,
        # then all of them together -- a design can be keyed by more than one at
        # once: `rr98_accuracy` is trials within blocks, where `trial` restarts
        # at 1 in each block, so neither column identifies a row alone and both
        # together identify it exactly. Same shape for a session x exercise
        # index. The `trial_*` reading was ruled 2026-09-19 (standard C5): the
        # 24 published trial tables index trials as `trial_number`,
        # `trial_num`, `trial_index` or `trial_block`, next to an `item` that
        # always identifies the probe.
        if any(f.check == "dup_id_item" for f in report.findings):
            resolved_by, _residual = resolve_occasion(df, occasion_columns(df))
            if resolved_by is not None:
                report.findings = [f for f in report.findings
                                   if f.check != "dup_id_item"]
                report.checks_run.append(f"dup_id_item:resolved_by_{resolved_by}")

    # run_qc now excludes nulls from its numeric denominator (#2314 item 2),
    # but retains the raw/core/triage 99% threshold. The gate profiles still
    # re-judge strictly: EVERY present value must parse. The inherited 99%
    # tolerance hid rare literal "NA" responses (#2029).
    if profile in ("upload", "legacy") and "resp" in df.columns:
        import pandas as pd
        present = df["resp"].dropna()
        invalid = present[pd.to_numeric(present, errors="coerce").isna()]
        report.findings = [f for f in report.findings if f.check != "resp_numeric"]
        if len(invalid):
            examples = ", ".join(repr(v)[:100] for v in invalid.drop_duplicates().head(5))
            report.findings.append(Finding(
                "resp_numeric", "error",
                f"{len(invalid)} non-numeric resp value(s) among {len(present)} "
                f"non-missing responses; examples: {examples}. Literal text "
                "tokens (including 'NA') are not empty cells. Verify their "
                "meaning in the source before recoding or removing rows.",
                table=table, group="core"))

    if profile in ("upload", "legacy"):
        for finding in (extra.check_name(table)
                        + extra.check_shape(df, table)
                        + extra.check_cov_range(df, table)
                        + extra.check_resp_dtype(df, table)
                        + extra.check_item_variants(df, table)):
            report.checks_run.append(finding.check)
            report.findings.append(finding)

    if {"id", "item", "resp"}.issubset(df.columns):
        try:
            report.stats = irw_metadata(df)
        except Exception:            # a metadata failure must not fail the gate
            report.stats = {}
    return report


def validate_file(path, *, label: str | None = None, profile: str = "upload",
                  max_bytes: int = MAX_BYTES, context: dict | None = None) -> Report:
    """Load a table from disk and validate it.

    Raises FileNotFoundError / ValueError for unusable input; the CLI turns
    those into exit code 2 rather than a misleading "failed validation".
    """
    path = Path(path)
    label = label or str(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    size = path.stat().st_size
    if size > max_bytes:
        report = Report(label=label, profile=profile)
        report.findings.append(Finding(
            "size_downgrade", "info",
            f"{size / 1024**2:.0f} MB exceeds the {max_bytes / 1024**2:.0f} MB "
            "cap for a full pandas pass; only the name checks ran. Validate it "
            "at processing time, where the frame is already in memory.",
            table=_table_name(label), group="name"))
        report.findings.extend(extra.check_name(_table_name(label)))
        return report

    import pandas as pd  # deferred: red_up must import this module without pandas
    if path.suffix.lower() in (".csv", ".tsv", ".txt"):
        df = pd.read_csv(path, sep=None, engine="python")
        if profile in ("upload", "legacy") and not is_item_text(label):
            if "resp" in df:
                # Re-read only resp without NA-token recognition. The Python
                # parser applies NA filtering even AFTER converters, so a
                # converter alone cannot preserve "NA" (#2029). A second,
                # single-column pass keeps every other column's established
                # parsing semantics, without retaining a second full frame.
                raw = pd.read_csv(path, sep=None, engine="python",
                                  usecols=["resp"], dtype={"resp": object},
                                  keep_default_na=False)["resp"]
                # Only empty fields are missing. Preserve whitespace and
                # literal NA/NULL/etc. as evidence; CSV quotes do not alter it.
                df["resp"] = raw.mask(raw == "")
                # Infer numeric storage for clean CSVs; never coerce invalid
                # tokens into nulls just to make the numeric check pass.
                try:
                    df["resp"] = pd.to_numeric(df["resp"], errors="raise")
                except (ValueError, TypeError):
                    pass  # validate_frame reports the preserved offending text
    elif path.suffix.lower() in (".rdata", ".rda", ".rds"):
        # The 922 legacy tables in ../data/pub/ (#1703 sub-item 1.5). Not
        # routed through irw_triage_updated.load_table because that pulls in
        # the whole discovery pipeline for a two-line read.
        try:
            import pyreadr
        except ImportError:
            raise ValueError(
                f"{path.name}: reading R data files needs pyreadr, which is "
                "optional -- install it with `pip install 'irw-validate[rdata]'`, "
                "or convert the table to CSV, which needs nothing extra."
            ) from None
        objs = pyreadr.read_r(str(path))
        if not objs:
            raise ValueError(f"{path.name} holds no R object")
        if len(objs) > 1:
            # An IRW table file should hold exactly one data frame. More than
            # one means the file is carrying something else besides the table,
            # and picking silently would validate the wrong object.
            raise ValueError(
                f"{path.name} holds {len(objs)} R objects "
                f"({', '.join(str(k) for k in objs)}); expected one table")
        df = next(iter(objs.values()))
    else:
        # Anything else goes through the pipeline's own reader, which exists
        # only in a checkout of ben-domingue/irw.
        root = _pipeline_root()
        if root is None:
            raise ValueError(
                f"{path.name}: '{path.suffix}' files are read by the IRW "
                "pipeline's loader, which is not part of this package -- it "
                "lives in a checkout of ben-domingue/irw. Convert the table to "
                "CSV, or run irw-validate from inside a checkout."
            )
        import sys
        sys.path.insert(0, str(root / "automated_finding"))
        from irw_triage_updated import load_table
        df = load_table(str(path))
    return validate_frame(df, label=label, profile=profile, context=context)


def validate_paths(paths, *, profile: str = "upload") -> list:
    return [validate_file(p, profile=profile) for p in paths]


def format_report(report: Report, *, show_passes: bool = False) -> str:
    """One block per table, errors first. Kept plain so CI logs stay readable."""
    lines = [f"{report.label} [{report.profile}]"]
    # Two verdicts, because they answer different questions: is this a valid
    # IRW table (the standard), and would IRW accept it (the profile's gate,
    # which adds intake policy such as the sample floor). A contributor's table
    # can pass the first and fail the second.
    if report.conforms is not None:
        verdict = "conforms" if report.conforms else \
            f"does not conform ({', '.join(report.nonconforming)})"
        lines.append(f"  IRW Data Standard {STANDARD_VERSION}: {verdict}")
        gate = "passes" if report.ok else f"blocked by {len(report.errors)} error(s)"
        lines.append(f"  IRW {report.profile} gate: {gate}")
    if not report.findings and not report.overridden:
        lines.append(f"  ok -- {len(report.checks_run)} checks, nothing to report")
    order = {"error": 0, "warn": 1, "info": 2}
    for f in sorted(report.findings, key=lambda f: order.get(f.severity, 3)):
        where = f"[{f.clause}]" if f.clause else ""
        lines.append(f"  {f.severity.upper():5s} {f.check:22s} {where:4s} {f.message}")
    for f in report.overridden:
        lines.append(f"  OVERRIDDEN {f.check:17s} {f.message}")
    if show_passes and report.checks_run:
        lines.append(f"  checks run: {', '.join(report.checks_run)}")
    return "\n".join(lines)
