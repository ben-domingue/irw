"""Checks for rankings tables (the `irw_rank` family, `source = "rank"`).

A rankings table keeps the core column names but `resp` is a position, not a
score: one row per respondent x task x marked position, `item` the option ranked
(a candidate code, or a reserved value), `resp` = 1 for the first choice. The
layout is the draft standard in `data/rankings/README.md`. Its rules are numbered
R1-R8 so they cannot be confused with the core standard's C1-C7 or conjoint's J1-J8.

The core checks would misread these tables (a position is not an ordered
response, and a repeated item within a ballot is allowed), so this module runs
instead of them: `red_up --dataset irw_rank` calls validate_rankings_file() with
the table's design row (checks.run_rankings_validator), and a collaborator can
check a table before sending it:

    python3 -m irw_validate.rankings table.csv [table.csv ...]
    python3 -m irw_validate.rankings --design data/rankings/design_tables.csv table.csv

With `--design`, R7 and R8 compare the table to its design record. Without it
they are skipped (not failed), so a table can be checked on its own first.

Exit codes as for `irw-validate`: 0 ok, 1 something blocks, 2 bad input.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from .extra import check_name

#: The rankings floor is 50 rankers, not the core 100 (Ben, 2026-10-15): a ranker
#: over three or more objects contributes several positions, so 50 rankings carry
#: at least as much information as 100 single responses on a short instrument.
MIN_IDS = 50
from .model import Finding, Report
from .pii import check_pii

REQUIRED = ("id", "task", "item", "resp")
PREFIXES = ("cov_", "trial_")
#: The reserved item values (data/rankings/README.md, "Layout").
RESERVED = {"(write-in)", "(overvote)"}
CODE = re.compile(r"^c\d{2,}$")
#: A candidate name is never stored; this catches the obvious case of one slipping
#: through (two or more capitalised words). A hint, not a rule: options that are
#: not people (policies, schools) are stored as text.
NAME_LIKE = re.compile(r"^[A-Z][a-zA-Z'.\-]+(\s+[A-Z][a-zA-Z'.\-]+)+$")


def _f(check: str, severity: str, message: str, table: str, details: tuple = ()) -> Finding:
    return Finding(check, severity, message, table=table, group="rankings", details=details)


def read_design(path) -> dict:
    with open(path, newline="", encoding="utf-8") as f:
        return {r["table"]: r for r in csv.DictReader(f)}


def validate_rankings_frame(df, *, label: str = "", design: dict | None = None) -> Report:
    """Check one rankings table against rules R1-R8 and the intake floor.

    `design` is this table's row of design_tables.csv (or None to skip R7-R8).
    """
    import pandas as pd
    table = Path(label).stem if label else ""
    report = Report(label=label, profile="upload", kind="rankings")
    out = report.findings
    cols = list(df.columns)
    report.checks_run = ["rank_required_columns", "rank_types", "rank_positions", "rank_items",
                         "rank_columns", "rank_design", "sample_floor"]

    # R1: required columns, no missing keys
    missing = [c for c in REQUIRED if c not in cols]
    if missing:
        out.append(_f("rank_required_columns", "error",
                      f"[R1] missing required column(s): {', '.join(missing)}", table))
        out.extend(check_name(table))
        return report
    for c in REQUIRED:
        n = int(df[c].isna().sum())
        if n:
            out.append(_f("rank_required_columns", "error", f"[R1] {n} rows with no {c}", table))

    # R2: resp and task are positive integers
    for c in ("resp", "task"):
        v = pd.to_numeric(df[c], errors="coerce")
        bad = int((v.isna() & df[c].notna()).sum() + ((v % 1 != 0) | (v < 1)).sum())
        if bad:
            out.append(_f("rank_types", "error", f"[R2] {c}: {bad} values that are not positive integers "
                          "(resp is the position marked, 1 = first choice)", table))

    # R3: within a ballot (id x task), a repeated position is a tie (equal ranks), allowed and reported
    # (Ben, 2026-10-15: ties may exist, as in competitions). An overvote is still one row.
    tied = df[df.duplicated(["id", "task", "resp"], keep=False)]
    report.stats["n_tied_ballots"] = int(tied.groupby(["id", "task"]).ngroups) if len(tied) else 0
    if len(tied):
        out.append(_f("rank_positions", "warning",
                      f"[R3] {report.stats['n_tied_ballots']} ballots rank two or more items equally "
                      f"({len(tied)} rows share a position); allowed, reported", table))

    # R4: items are codes, reserved values, or option text; never a person's name
    items = df["item"].dropna().astype(str)
    paren = sorted(set(items[items.str.startswith("(")]) - RESERVED)
    if paren:
        out.append(_f("rank_items", "error",
                      f"[R4] item value(s) in parentheses that are not reserved: {paren[:5]}; "
                      f"the reserved values are exactly {sorted(RESERVED)}", table, tuple(paren)))
    blank = int((items.str.strip() == "").sum())
    if blank:
        out.append(_f("rank_items", "error", f"[R4] {blank} blank item values", table))
    named = sorted(set(items[items.map(lambda s: bool(NAME_LIKE.match(s)))]))
    if named:
        out.append(_f("rank_items", "error",
                      f"[R4] item value(s) that look like personal names: {named[:5]}; candidates are "
                      "coded c01, c02, ... in alphabetical order (README, 'Candidate codes')", table, tuple(named)))
    codes = items[items.map(lambda s: bool(CODE.match(s)))]
    if len(codes):
        widths = set(codes.str.len())
        if len(widths) > 1:
            out.append(_f("rank_items", "error",
                          f"[R4] candidate codes of mixed width: {sorted(set(codes))[:6]}", table))
    # duplicate marks are allowed (README): report them
    marks = df.groupby(["id", "task", "item"]).size()
    report.stats["n_duplicate_marks"] = int((marks - 1).clip(lower=0).sum())

    # R6: column names
    undefined = [c for c in cols if c not in REQUIRED and not c.startswith(PREFIXES)]
    if undefined:
        out.append(_f("rank_columns", "error",
                      f"[R6] column(s) with no defined meaning: {', '.join(undefined)}", table, tuple(undefined)))
    for c in cols:
        if c.startswith("cov_"):
            g = df.groupby(["id", "task"])[c].nunique(dropna=False)
            if (g > 1).any():
                out.append(_f("rank_columns", "error",
                              f"[R6] {c} varies within a ballot; cov_ columns are ballot-level", table, (c,)))

    # R7, R8: the design record
    if design is not None:
        try:
            npos = int(design["n_positions"])
            over = int((pd.to_numeric(df["resp"], errors="coerce") > npos).sum())
            if over:
                out.append(_f("rank_design", "error",
                              f"[R7] {over} rows with resp above n_positions = {npos} in the design record", table))
            ncand = int(design["n_candidates"])
            seen = len(set(codes))
            if seen and seen != ncand:
                out.append(_f("rank_design", "error",
                              f"[R8] {seen} candidate codes in the table, n_candidates = {ncand} in the design record",
                              table))
            nb = int(design["n_ballots_with_marks"])
            if df["id"].nunique() != nb:
                out.append(_f("rank_design", "error",
                              f"[R8] {df['id'].nunique()} ids in the table, n_ballots_with_marks = {nb} in the "
                              "design record", table))
        except (KeyError, ValueError) as exc:
            out.append(_f("rank_design", "error", f"[R7] design record unreadable: {exc}", table))

    # intake policy and stats
    n = int(df["id"].nunique())
    report.stats["n_ballots"] = n
    if n < MIN_IDS:
        out.append(_f("sample_floor", "warn",
                      f"{n} unique ids; the rankings family floor is {MIN_IDS} rankers (README, Intake rules)", table))
    per = df.groupby(["id", "task"]).size()
    report.stats["marks_per_ballot"] = {int(k): int(v) for k, v in per.value_counts().sort_index().items()}
    gaps = df.groupby(["id", "task"])["resp"].agg(lambda s: int(s.max() - len(s)) if len(s) else 0)
    report.stats["n_ballots_with_gap"] = int((gaps > 0).sum())
    report.stats["n_rows"] = int(len(df))
    out.extend(check_name(table))
    # The write-path PII screen (#3227). The registry had no PII check for any
    # family, so a table arriving by any route other than automated-finding
    # triage reached Redivis unscreened; see irw_validate/pii.py for why a
    # value match fails and a name match warns.
    _findings, _checks = check_pii(df, report.label or "")
    report.checks_run.extend(_checks)
    report.findings.extend(_findings)
    return report


def validate_rankings_file(path, *, label: str | None = None, design: dict | None = None) -> Report:
    import pandas as pd
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, low_memory=False, keep_default_na=False, na_values=[""])
    return validate_rankings_frame(df, label=label or str(path), design=design)


def main(argv=None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    designs = None
    if "--design" in args:
        i = args.index("--design")
        designs = read_design(args[i + 1])
        del args[i:i + 2]
    if not args:
        print(__doc__.strip().splitlines()[0])
        print("usage: python3 -m irw_validate.rankings [--design design_tables.csv] table.csv [...]")
        return 2
    worst = 0
    for p in args:
        stem = Path(p).stem
        design = None
        if designs is not None:
            design = designs.get(stem)
            if design is None:
                print(f"{p}: no row in the design record (R7); add one before sending the table")
                worst = max(worst, 1)
        try:
            r = validate_rankings_file(p, design=design)
        except (FileNotFoundError, ValueError) as exc:
            print(f"{p}: cannot read ({exc})")
            worst = max(worst, 2)
            continue
        status = "blocked" if r.errors else "passes"
        s = r.stats
        print(f"{p}: {status} (rankings draft standard; {s.get('n_ballots', '?')} ballots, {s.get('n_rows', '?')} rows, "
              f"{s.get('n_duplicate_marks', 0)} duplicate marks, {s.get('n_ballots_with_gap', 0)} ballots with a gap)")
        for f in r.findings:
            print(f"  {f.severity.upper():5} {f.check:22} {f.message}")
        if r.errors:
            worst = max(worst, 1)
    return worst


if __name__ == "__main__":
    sys.exit(main())
