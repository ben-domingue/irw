"""`irw-validate` -- check IRW tables and exit non-zero if anything blocks.

    irw-validate out/*.csv
    irw-validate out/                            # every table directly in out/
    irw-validate -r .                            # ...and in every subdirectory
    irw-validate out/x.csv --profile core        # the validate_irw.R subset
    irw-validate out/x.csv --strict              # warnings block too
    irw-validate out/x.csv --json                # machine-readable, for CI
    irw-validate out/x.csv --override-check resp_scale_mixed \\
        --override "two response formats, one construct; author confirmed 2026-09-02"

Exit codes, matching red_up's contract: 0 ok - 1 something blocks - 2 bad input.

**On the override.** The reason is the flag's *argument*, so overriding without
saying why is structurally impossible. The flag is not called `--force` or
`--no-verify`: those names invite reflex use, and the point is to make a waiver
a decision someone signed. Overridden findings are reprinted under OVERRIDDEN
rather than suppressed, and the reason is appended to
`processing_notes/validator_overrides.csv` so a waiver leaves a trail even when
nobody keeps the terminal output.

This formalises something that already happens informally: `data/cao_2026_cdss.py`
waives `resp_scale_mixed` in a prose comment -- correct judgment, recorded where
no tool can read it.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import getpass
import json
import sys
from pathlib import Path

from .core import TABLE_SUFFIXES, format_report, validate_file
from .model import PROFILES, exit_code

MIN_REASON = 20
#: Where waivers are recorded. Overridable so a test run -- or anyone working
#: outside a checkout -- does not append to the repository's ledger.
LEDGER_ENV = "IRW_VALIDATE_LEDGER"
_DEFAULT_LEDGER = (Path(__file__).resolve().parent.parent
                   / "processing_notes" / "validator_overrides.csv")


def ledger_path() -> Path:
    import os
    return Path(os.environ.get(LEDGER_ENV) or _DEFAULT_LEDGER)


def _record(reasons_path: Path, rows: list) -> None:
    """Append waivers to the ledger. Never fatal -- a gate that fails because
    it could not write its own audit file would be worse than the gap."""
    try:
        reasons_path.parent.mkdir(parents=True, exist_ok=True)
        new = not reasons_path.exists()
        with reasons_path.open("a", newline="") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["date", "tool", "table", "checks", "reason", "user"])
            w.writerows(rows)
    except OSError as exc:
        print(f"warning: could not write {reasons_path}: {exc}", file=sys.stderr)


#: What a directory walk picks up. `.txt` is left out although `validate_file`
#: reads it: in a submission folder a `.txt` is a README far more often than a
#: table, and a README that fails to parse would turn `irw-validate -r .` into
#: exit 2. Name a `.txt` table explicitly and it is read as before.
DIR_SUFFIXES = tuple(s for s in TABLE_SUFFIXES if s != ".txt")
#: Archive debris, never tables: macOS zips add `__MACOSX/._<name>.csv`, a
#: resource fork that has a table's extension and none of its content.
_SKIP_DIRS = {"__MACOSX", ".git", "__pycache__"}


def expand_paths(paths: list, recursive: bool = False) -> tuple[list, list]:
    """Turn the command-line paths into the files to validate.

    A file is taken as given, whatever its extension -- naming it is the
    caller saying it is a table. A directory contributes the table files
    directly inside it, or everywhere below it with `recursive`; anything else
    in there (READMEs, codebooks, hidden files) is skipped without comment.
    Returns (files, empty_dirs): a directory holding no table at all is
    reported by the caller rather than passing as an empty success.
    """
    files, empty = [], []
    for raw in paths:
        p = Path(raw)
        if not p.is_dir():
            files.append(str(p))
            continue
        found = []
        walk = p.rglob("*") if recursive else p.iterdir()
        for f in walk:
            rel = f.relative_to(p).parts
            if any(part.startswith(".") or part in _SKIP_DIRS for part in rel):
                continue
            if f.is_file() and f.name.lower().endswith(DIR_SUFFIXES):
                found.append(str(f))
        if found:
            files.extend(sorted(found))
        else:
            empty.append(str(p))
    seen = set()
    return [f for f in files if not (f in seen or seen.add(f))], empty


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="irw-validate",
        description="Validate IRW tables against the data standard.")
    ap.add_argument("paths", nargs="+",
                    help="CSV (or any format load_table reads), or a directory "
                         "of them")
    ap.add_argument("-r", "--recursive", action="store_true",
                    help="also validate tables in subdirectories of a directory "
                         "argument")
    ap.add_argument("--profile", default="upload", choices=PROFILES,
                    help="core = the validate_irw.R subset; triage = today's "
                         "run_qc behaviour; upload = the gate (default); "
                         "legacy = upload minus rules that postdate the table")
    ap.add_argument("--strict", action="store_true",
                    help="warnings block too")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--override", metavar="REASON",
                    help=f"waive blocking findings, giving a reason of at least "
                         f"{MIN_REASON} characters")
    ap.add_argument("--override-check", action="append", metavar="NAME", default=[],
                    help="limit --override to this check (repeatable); without "
                         "it, --override waives every error")
    args = ap.parse_args(argv)

    if args.override_check and not args.override:
        print("irw-validate: --override-check needs --override REASON",
              file=sys.stderr)
        return 2
    if args.override is not None and len(args.override.strip()) < MIN_REASON:
        print(f"irw-validate: that is not a reason -- give at least "
              f"{MIN_REASON} characters saying why this table is an exception",
              file=sys.stderr)
        return 2

    paths, empty = expand_paths(args.paths, recursive=args.recursive)
    for d in empty:
        hint = "" if args.recursive else " (use -r to look in subdirectories)"
        print(f"irw-validate: no table files ({', '.join(DIR_SUFFIXES)}) "
              f"in {d}{hint}", file=sys.stderr)
    if empty:
        return 2

    reports = []
    for path in paths:
        try:
            reports.append(validate_file(path, profile=args.profile))
        except FileNotFoundError:
            print(f"irw-validate: no such file: {path}", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"irw-validate: cannot read {path}: {exc}", file=sys.stderr)
            return 2

    ledger_rows = []
    if args.override:
        wanted = set(args.override_check)
        for report in reports:
            waived = [f for f in report.errors
                      if not wanted or f.check in wanted]
            if not waived:
                continue
            report.findings = [f for f in report.findings if f not in waived]
            report.overridden.extend(waived)
            report.override_reason = args.override
            ledger_rows.append([
                dt.date.today().isoformat(), "irw-validate", report.label,
                ";".join(sorted({f.check for f in waived})), args.override,
                getpass.getuser(),
            ])
    if ledger_rows:
        _record(ledger_path(), ledger_rows)

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2))
    else:
        for report in reports:
            print(format_report(report))

    code = exit_code(reports, strict=args.strict)
    if code and not args.json:
        blocking = sum(len(r.errors) for r in reports)
        if blocking:
            print(f"\n{blocking} blocking finding(s). Fix them, or waive with "
                  f"--override \"<why>\".", file=sys.stderr)
        else:
            print("\n--strict: warnings are blocking.", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
