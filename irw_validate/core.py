"""The public API: validate a frame or a file, get a Report with an exit code."""
from __future__ import annotations

import os
from pathlib import Path

from . import extra
from ._checks import irw_metadata, run_qc
from .model import Finding, Report, severity_for

#: Above this, a full pandas load is not worth it inside the uploader's hot
#: path -- red_up streams 500 MB tables with the csv module on purpose. Files
#: over the cap get a core-only streaming pass and an explicit `info` finding
#: recording the downgrade, so a skipped check is never silent.
MAX_BYTES = 512 * 1024 ** 2


#: Every extension a table can arrive as. Matched case-insensitively: the legacy
#: files are `.Rdata`, and stripping only `.csv` made every one of the 922 fail
#: the lowercase-name rule on the capital R of its own extension.
TABLE_SUFFIXES = (".csv", ".tsv", ".txt", ".rdata", ".rda", ".rds")


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


def _validate_item_text(df, label: str, profile: str) -> Report:
    """The item text schema: check what applies, and say nothing about the rest."""
    report = Report(label=label, profile=profile)
    table = _table_name(label)[: -len(ITEMS_SUFFIX)]
    missing = [c for c in ITEMS_REQUIRED if c not in df.columns]
    report.checks_run.append("required_columns")
    if missing:
        report.findings.append(Finding(
            "required_columns", "error",
            f"missing required columns for item text: {', '.join(missing)}",
            table=table, group="core"))
        return report
    keys = [c for c in ("item", "resp") if c in df.columns]
    report.checks_run.append("dup_item_resp")
    dup = int(df.duplicated(subset=keys).sum()) if keys else 0

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
    if scored:
        exact = int(df.duplicated().sum())
        if exact:
            report.findings.append(Finding(
                "dup_row", "error",
                f"{exact} fully identical row(s) in a scored table. `resp` here is a "
                f"scoring key, so one value carrying several option labels is "
                f"expected -- but an exact repeat is still a duplicate.",
                table=table, group="core"))
    elif dup:
        # Two different faults produce this, and the distinction matters to
        # whoever has to fix it, so name which one this is. If the repeated rows
        # carry the SAME option_text it is a doubled upload (#1810/#1816). If
        # they carry DIFFERENT option_text, the table is asserting that one
        # response value means two things -- afps_vangsness_2019 maps resp=1 to
        # both "Strongly agree" and "Strongly disagree", which is two opposite
        # scale directions written into one table and is worse than a duplicate.
        conflicting = 0
        if "option_text" in df.columns:
            per_key = df.groupby(keys)["option_text"].nunique(dropna=False)
            conflicting = int((per_key > 1).sum())
        if conflicting:
            report.findings.append(Finding(
                "resp_ambiguous", "error",
                f"{conflicting} response value(s) carry more than one option label -- "
                f"the same `resp` is documented as meaning two different things, so "
                f"nothing joining item text to responses can resolve it. Usually two "
                f"opposite scale directions merged into one table.",
                table=table, group="core"))
        else:
            report.findings.append(Finding(
                "dup_item_resp", "error",
                f"{dup} duplicate item+resp rows with identical option text -- an item "
                f"text table carries one row per response option, so a repeat is a "
                f"doubled upload (#1810)",
                table=table, group="core"))
    for finding in extra.check_name(table):
        report.checks_run.append(finding.check)
        report.findings.append(finding)
    report.stats = {"n_rows": len(df),
                    "n_items": int(df["item"].nunique()) if "item" in df else 0}
    return report


def validate_frame(df, *, label: str = "", profile: str = "upload",
                   context: dict | None = None) -> Report:
    """Run every check the profile asks for against an in-memory frame."""
    context = context or {}
    if is_item_text(label):
        return _validate_item_text(df, label, profile)
    report = Report(label=label, profile=profile)
    table = _table_name(label)

    for check in run_qc(df,
                        coercion_method=context.get("coercion_method", ""),
                        original_cols=context.get("original_cols")):
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
        occasion_cols = ("rater", "wave", "timepoint", "date", "trialnum", "trial",
                         "order", "session", "occasion", "period", "block", "subtest")
        if any(f.check == "dup_id_item" for f in report.findings):
            resolved_by = None
            for col in occasion_cols:
                if col in df.columns and not df.duplicated(subset=["id", "item", col]).any():
                    resolved_by = col
                    break
            # A design can be keyed by more than one occasion column at once, and
            # testing them only one at a time misses that. `rr98_accuracy` is
            # trials within blocks: `trial` restarts at 1 in each block, so
            # neither column identifies a row alone and both together identify
            # it exactly. Same shape for a session x exercise index. So if no
            # single column resolves the repeat, try every occasion column
            # present together before calling it a defect.
            if resolved_by is None:
                present = [c for c in occasion_cols if c in df.columns]
                if len(present) > 1 and not df.duplicated(
                        subset=["id", "item"] + present).any():
                    resolved_by = "+".join(present)
            if resolved_by is not None:
                report.findings = [f for f in report.findings
                                   if f.check != "dup_id_item"]
                report.checks_run.append(f"dup_id_item:resolved_by_{resolved_by}")

    # `resp_numeric` as inherited from run_qc measures how many values parse as
    # numbers over ALL rows, so a float column with missing values fails it --
    # NaN does not parse. That conflates "not a number" with "not present", and
    # `resp_na` already reports the second. In the legacy sweep it flagged
    # 16_personalityfactors, whose resp is float64 and 99% non-null.
    #
    # Triage keeps the inherited behaviour (50 callers depend on it); the gate
    # profiles re-judge it over non-null values only.
    if profile in ("upload", "legacy") and "resp" in df.columns:
        import pandas as pd
        present = df["resp"].dropna()
        if len(present):
            parses = pd.to_numeric(present, errors="coerce").notna().mean()
            if parses >= 0.99:
                report.findings = [f for f in report.findings if f.check != "resp_numeric"]

    if profile in ("upload", "legacy"):
        for finding in (extra.check_name(table)
                        + extra.check_shape(df, table)
                        + extra.check_cov_range(df, table)
                        + extra.check_resp_dtype(df, table)):
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
    elif path.suffix.lower() in (".rdata", ".rda", ".rds"):
        # The 922 legacy tables in ../data/pub/ (#1703 sub-item 1.5). Not
        # routed through irw_triage_updated.load_table because that pulls in
        # the whole discovery pipeline for a two-line read.
        import pyreadr
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
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "automated_finding"))
        from irw_triage_updated import load_table
        df = load_table(str(path))
    return validate_frame(df, label=label, profile=profile, context=context)


def validate_paths(paths, *, profile: str = "upload") -> list:
    return [validate_file(p, profile=profile) for p in paths]


def format_report(report: Report, *, show_passes: bool = False) -> str:
    """One block per table, errors first. Kept plain so CI logs stay readable."""
    lines = [f"{report.label} [{report.profile}]"]
    if not report.findings and not report.overridden:
        lines.append(f"  ok -- {len(report.checks_run)} checks, nothing to report")
    order = {"error": 0, "warn": 1, "info": 2}
    for f in sorted(report.findings, key=lambda f: order.get(f.severity, 3)):
        lines.append(f"  {f.severity.upper():5s} {f.check:22s} {f.message}")
    for f in report.overridden:
        lines.append(f"  OVERRIDDEN {f.check:17s} {f.message}")
    if show_passes and report.checks_run:
        lines.append(f"  checks run: {', '.join(report.checks_run)}")
    return "\n".join(lines)
