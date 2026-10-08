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
import hashlib
import os
import re
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


def run_validator(path: Path, context: dict | None = None) -> tuple[list[str], list[str]]:
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
        report = validate_file(path, profile="upload", context=context)
    except Exception as exc:                      # unreadable, odd encoding, ...
        return ([f"validator could not read this file: {exc}"], [])

    return ([f"{f.check}: {f.message}" for f in report.errors],
            [f"{f.check}: {f.message}" for f in report.warnings])


def run_conjoint_validator(path: Path, opt_out: dict | None = None) -> tuple[list[str], list[str]]:
    """The conjoint-table checks (irw_validate.conjoint). -> (errors, warnings)

    A conjoint table has no item/resp, so the core validator would fail every
    one on C1. Same failure rules as run_validator: a missing dependency or an
    unreadable file is an error, never a pass. `opt_out` (from conj_opt_out)
    settles J3's "no chosen profile" warning: an error where the design had no
    opt-out, silent where it had one.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    try:
        from irw_validate.conjoint import validate_conjoint_file
    except ImportError as exc:
        return ([f"conjoint validator unavailable ({exc}) -- install pandas, or pass "
                 f"--no-validate to upload without a format check"], [])
    try:
        report = validate_conjoint_file(path, opt_out=opt_out)
    except Exception as exc:
        return ([f"conjoint validator could not read this file: {exc}"], [])
    return ([f"{f.check}: {f.message}" for f in report.errors],
            [f"{f.check}: {f.message}" for f in report.warnings])


#: The conjoint design records (data/conjoint/README.md, "Design records" and
#: "Attribute crosswalk"). IRW_CONJ_DESIGN_DIR points the check at another
#: directory, for tests; production never sets it.
def _conj_design_dir() -> Path:
    env = os.environ.get("IRW_CONJ_DESIGN_DIR")
    return Path(env) if env else Path(__file__).resolve().parent.parent / "data" / "conjoint"


_CONJ_OUTCOME = re.compile(r"^(choice|rating)(_.+)?$")


def conj_opt_out(table: str) -> dict[str, str]:
    """{choice column: opt_out} for one table, from design_outcomes.csv.

    Empty when the records cannot be read: check_conj_design reports that as an
    error, and the validator then falls back to warning, as it does standalone.
    """
    try:
        with open(_conj_design_dir() / "design_outcomes.csv", newline="", encoding="utf-8") as f:
            return {r["outcome"]: (r.get("opt_out") or "unknown").strip()
                    for r in csv.DictReader(f)
                    if r["table"] == table and r.get("type", "choice") == "choice"}
    except (OSError, KeyError):
        return {}


def check_conj_design(report: FileReport) -> tuple[list[str], list[str]]:
    """A conjoint table needs its design records before it goes up. -> (errors, warnings)

    Errors: no row in design_tables.csv, or an outcome column with no row in
    design_outcomes.csv -- without them the table cannot be pooled with the
    others (conj_metadata/conj_outcomes would carry NA for it), and nothing
    later forces anyone to come back. Warnings: an outcome row for a column the
    file lacks (stale), and a gender attribute with no crosswalk.csv rows.
    Unreadable records are an error, never a pass.
    """
    d = _conj_design_dir()
    try:
        with open(d / "design_tables.csv", newline="", encoding="utf-8") as f:
            tables = {r["table"] for r in csv.DictReader(f)}
        with open(d / "design_outcomes.csv", newline="", encoding="utf-8") as f:
            outcomes = {(r["table"], r["outcome"]) for r in csv.DictReader(f)}
        with open(d / "crosswalk.csv", newline="", encoding="utf-8") as f:
            crosswalk = {(r["table"], r["attribute"]) for r in csv.DictReader(f)}
    except (OSError, KeyError) as exc:
        return ([f"conj design records unreadable in {d} ({exc})"], [])
    t, cols = report.table, report.columns
    errors, warnings = [], []
    where = "data/conjoint/README.md, \"Design records\""
    if t not in tables:
        errors.append(f"conj_design: {t} has no row in design_tables.csv ({where})")
    have = [c for c in cols if _CONJ_OUTCOME.match(c)]
    missing = [c for c in have if (t, c) not in outcomes]
    if missing:
        errors.append(f"conj_design: outcome column(s) with no row in design_outcomes.csv: "
                      f"{', '.join(missing)} ({where})")
    stale = sorted(o for (tt, o) in outcomes if tt == t and o not in have)
    if stale:
        warnings.append(f"conj_design: design_outcomes.csv has row(s) for column(s) this file "
                        f"lacks: {', '.join(stale)}")
    for a in ("attr_gender", "attr_sex"):
        if a in cols and (t, a) not in crosswalk:
            warnings.append(f"conj_crosswalk: {a} has no rows in crosswalk.csv "
                            f"(profile_gender); add them so the table pools with the others")
    return errors, warnings


def validate_for_target(report: FileReport, target: Target,
                        enabled: bool = True, context: dict | None = None) -> None:
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

    `context` is passed through to the validator; the CLI supplies
    `permitted_values` from the table's item text (#2152, see permitted.py).
    """
    if not enabled or not required_columns(target):
        return
    if report.errors:
        return                # a file that is not a table yet is not worth validating
    if target.source == "conj":
        errors, warnings = run_conjoint_validator(report.path, conj_opt_out(report.table))
        report.errors.extend(errors)
        report.warnings.extend(warnings)
        errors, warnings = check_conj_design(report)
        report.errors.extend(errors)
        report.warnings.extend(warnings)
        return
    errors, warnings = run_validator(report.path, context)
    report.errors.extend(errors)
    report.warnings.extend(warnings)


#: A directory holding this file is a record of an extraction, not a place
#: uploads are staged from. Item text is where this bit us (see
#: itemtext/BATCH_PROCESS.md: batches are history, `clean/` is staging), but
#: the rule is stated about the marker file rather than about that path, so
#: red_up stays general-purpose and any tree with the same convention is
#: covered.
HISTORY_MARKER = "provenance.csv"


def history_dirs(csvs: list[Path]) -> list[Path]:
    """Directories among `csvs` that are batch history rather than staging.

    The collision check in `check_all` is NOT a backstop for this. It only
    fires when two batches happen to hold the same table name; a walk over a
    tree whose names are all distinct uploads the entire extraction history
    without a word -- and because a Redivis upload appends, re-uploading an
    already-shipped table doubles it rather than doing nothing (#2055).

    Reported per directory rather than as a boolean: a run over `itemtables/`
    picks up thirty-odd of them at once, and the useful message names the tree,
    not the first file in it.
    """
    dirs = {p.parent for p in csvs if p.name != HISTORY_MARKER}
    return sorted(d for d in dirs if (d / HISTORY_MARKER).is_file())


def check_all(pairs: list[tuple[Path, str]]) -> list[FileReport]:
    """Scan every file, and flag names that collide within the batch itself.

    Deliberately target-blind: it runs before the destination is chosen, so
    every check here must hold for any destination. Anything that depends on
    where the file is going belongs in check_schema or validate_for_target.

    Two files with the same stem in different subdirectories would upload one
    after the other into the same table name. Because a Redivis upload APPENDS,
    that is not "the second one wins" -- it is a doubled table. So it stays an
    error even when the files are byte-identical, and especially then.

    The message says whether the colliding files have the same content, because
    that is the first thing anyone asks and the answer decides what to do:

      - IDENTICAL content is usually not a batch-assembly mistake at all. A
        re-issued batch keeps an unchanged copy of the CSV alongside its new
        provenance row (see itemtext/BATCH_PROCESS.md), so the same table
        legitimately appears in two batch directories. The fix is to point the
        uploader at the staging directory instead of walking batch history --
        NOT to delete either copy. irw#1962 spent its whole life on the other
        reading, and deleting the "stale" copy there would have destroyed the
        record of a hold release.
      - DIFFERING content is the real batch-assembly mistake: two versions of a
        table are in flight and someone has to say which one is right.
    """
    reports = [scan(path, table) for path, table in pairs]

    seen: dict[str, list[FileReport]] = {}
    for report in reports:
        seen.setdefault(report.table, []).append(report)
    for table, group in seen.items():
        if len(group) > 1:
            others = ", ".join(str(r.path) for r in group)
            if _all_identical(r.path for r in group):
                detail = (
                    "byte-identical content, so this is probably batch history "
                    "rather than two competing versions -- upload from the "
                    "staging directory rather than deleting a copy"
                )
            else:
                detail = "DIFFERING content -- decide which version is right"
            for report in group:
                report.errors.append(
                    f"table name '{table}' is claimed by {len(group)} files "
                    f"({detail}): {others}"
                )
    return reports


def _all_identical(paths) -> bool:
    """True when every path has the same bytes.

    Hashes rather than compares pairwise: a collision group can be larger than
    two, and these files run to hundreds of MB, so read each one once and in
    chunks. An unreadable file returns False -- "cannot prove identical" is the
    safe answer, and it keeps the caller on the louder message.
    """
    digests = set()
    for path in paths:
        digest = hashlib.sha256()
        try:
            with open(path, "rb") as handle:
                for chunk in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(chunk)
        except OSError:
            return False
        digests.add(digest.hexdigest())
        if len(digests) > 1:
            return False
    return True
