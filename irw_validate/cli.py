"""`irw-validate` -- check IRW tables and exit non-zero if anything blocks.

    irw-validate out/*.csv
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

from .core import format_report, validate_file
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


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="irw-validate",
        description="Validate IRW tables against the data standard.")
    ap.add_argument("paths", nargs="+", help="CSV (or any format load_table reads)")
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

    reports = []
    for path in args.paths:
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
