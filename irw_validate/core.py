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


def _table_name(label: str) -> str:
    stem = Path(label).name
    for suffix in (".csv", ".tsv"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
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
    for name, dup in (("dup_item_resp",
                       df.duplicated(subset=[c for c in ("item", "resp")
                                             if c in df.columns]).sum()),):
        report.checks_run.append(name)
        if dup:
            report.findings.append(Finding(
                name, "error",
                f"{dup} duplicate item+resp rows -- an item text table carries one "
                f"row per response option, so a repeat is a doubled upload (#1810)",
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
