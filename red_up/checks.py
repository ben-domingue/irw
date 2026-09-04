"""Local checks run before anything is uploaded.

Deliberately the cheap half of "one validator, one uploader, and a gate
between them" (#1703). Unifying misc/validate_irw.R with
automated_finding/irw_triage_updated.py::run_qc() is sub-item 1.3 and a
separate piece of work; `run_validator` below is the seam it plugs into.

Everything here streams with the csv module rather than pandas: some of these
tables are hundreds of MB and the only thing we need is a row count and a
header.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .targets import Target, required_columns


@dataclass
class FileReport:
    path: Path
    table: str
    rows: int = 0            # data rows, header excluded
    columns: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def scan(path: Path, table: str) -> FileReport:
    """Read a CSV once: header, column count, data-row count.

    Schema is *not* checked here -- what a table must contain depends on where
    it is going (see check_schema), and the destination is not known until the
    files have been read.

    The row count is not cosmetic -- it is the number verify.py asserts the
    uploaded table against, and the reason numRows is never consulted.
    """
    report = FileReport(path=path, table=table)
    try:
        with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration:
                report.errors.append("file is empty (no header)")
                return report
            report.columns = [c.strip() for c in header]
            report.rows = sum(1 for _ in reader)
    except OSError as exc:
        report.errors.append(f"unreadable: {exc}")
        return report

    if report.rows == 0:
        report.errors.append("no data rows")

    if table != table.lower():
        # Case is a live trap here: 307 non-lowercase table names drop out of
        # any case-sensitive metadata join, and item text has already gone
        # astray this way (pezzuti_2025_..._SouthKorea vs ..._southkorea).
        report.warnings.append("name is not lowercase (breaks case-sensitive metadata joins)")
    if table != table.strip() or " " in table:
        report.warnings.append("name contains whitespace")

    return report


def check_schema(report: FileReport, target: Target) -> None:
    """Check a scanned file against the schema its destination expects.

    Missing *some* required columns is a warning -- the table is recognisably
    an IRW table with a problem, and you may be fixing that separately.
    Missing *all* of them is an error: that is a notes/provenance/audit file
    that happens to end in .csv, and uploading it is the exact failure
    `itemtext/itemtables/clean/` was created to undo.
    """
    required = required_columns(target)
    if not required or not report.columns:
        return
    missing = [c for c in required if c not in report.columns]
    if len(missing) == len(required):
        report.errors.append(
            f"none of the required columns ({', '.join(required)}) are present "
            "-- this does not look like a table for " + target.name)
    elif missing:
        report.warnings.append(f"missing required column(s): {', '.join(missing)}")


def run_validator(path: Path) -> tuple[list[str], list[str]]:
    """The full IRW format validator (#1703 sub-item 1.3). -> (errors, warnings)

    Everything above this streams with the csv module because some of these
    tables are hundreds of MB. The validator needs pandas and a whole frame, so
    it is imported lazily and skips above `irw_validate.MAX_BYTES` -- and when
    it skips, it says so as a warning rather than passing quietly.

    A missing dependency is an ERROR, never a pass. Blocking because pandas is
    not installed is annoying exactly once; passing because pandas is not
    installed is undetectable forever.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    try:
        from irw_validate import validate_file
    except ImportError as exc:
        return ([f"validator unavailable ({exc}) -- install pandas, or pass "
                 f"--no-validate to upload without a format check"], [])

    try:
        report = validate_file(path, profile="upload")
    except Exception as exc:                      # unreadable, odd encoding, ...
        return ([f"validator could not read this file: {exc}"], [])

    return ([f"{f.check}: {f.message}" for f in report.errors],
            [f"{f.check}: {f.message}" for f in report.warnings])


def validate_for_target(report: FileReport, target: Target,
                        enabled: bool = True) -> None:
    """Run the full IRW format validator, where the target expects that format.

    This has to happen HERE, next to check_schema, and not in check_all --
    which is the bug that made every `irw_meta` upload a no-op between
    2026-09-02 and 2026-09-03. `irw_validate` enforces `id`/`item`/`resp`, so
    it is a check about the destination's schema, and check_all runs before a
    destination has been chosen. Metadata tables have no such columns and are
    exempt by design; run from check_all, the validator failed all thirteen of
    them and red_up reported "nothing here belongs in irw_meta".

    One rule, one place: a target with no required columns is a target whose
    tables have no common schema, so there is nothing for a format validator to
    say about them. That is the same condition check_schema returns early on.
    """
    if not enabled or not required_columns(target):
        return
    if report.errors:
        return                # a file that is not a table yet is not worth validating
    errors, warnings = run_validator(report.path)
    report.errors.extend(errors)
    report.warnings.extend(warnings)


def check_all(pairs: list[tuple[Path, str]]) -> list[FileReport]:
    """Scan every file, and flag names that collide within the batch itself.

    Deliberately target-blind: it runs before the destination is chosen, so
    every check here must hold for any destination. Anything that depends on
    where the file is going belongs in check_schema or validate_for_target.

    Two files with the same stem in different subdirectories would upload one
    after the other into the same table name, and the second would silently
    win. That is a batch-assembly mistake, so it is an error, not a warning.
    """
    reports = [scan(path, table) for path, table in pairs]

    seen: dict[str, list[FileReport]] = {}
    for report in reports:
        seen.setdefault(report.table, []).append(report)
    for table, group in seen.items():
        if len(group) > 1:
            others = ", ".join(str(r.path) for r in group)
            for report in group:
                report.errors.append(
                    f"table name '{table}' is claimed by {len(group)} files: {others}"
                )
    return reports
