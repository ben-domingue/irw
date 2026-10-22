#!/usr/bin/env python3
##Minneapolis ranked-choice ballot totals: count the ballots in each FairVote raw file and compare the counts with the
##table's design row and, where you give it, with the total the city prints.
##
##Usage:
##  python3 ballot_totals.py --design ../design_tables.csv --raw-dir <dir> [--prefix rcv_mpls_20231107_ | TABLE ...] \
##      [--expect TABLE=N ...]
##
##The raw file of a table is <raw-dir>/<source_file of its design row>. The counts use the definitions of
##fairvote_cvr.py (the columns n_ballots_cast ... n_writeins of design_tables.csv):
##  ballots      rows of the raw file (n_ballots_cast)
##  with_marks   rows with at least one mark (n_ballots_with_marks)
##  overvotes    cells that hold an overvote (n_overvotes)
##  writeins     cells that hold a write-in (n_writeins)
##  duplicates   marks that repeat an item already marked on the same ballot, overvote and write-in cells included
##               (n_duplicate_marks)
##A cell is a mark unless it is `skipped` or `undervote`. Spelling of the tokens is ignored (spaces, hyphens and case).
##--expect TABLE=N says what the city prints as the total for the contest, and `ballots` must equal it. Read it from the
##city's results page: "Total ballots cast" for a contest decided on first choices. A page that prints "Total votes cast"
##and "Undervotes" separately gives their sum. The script only compares the numbers you give it.
##No candidate name is printed or kept: only counts.
##Exit code: 0 everything equal, 1 something differs, 2 bad input.
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

TOKENS = {"skipped": None, "undervote": None, "overvote": "(overvote)", "writein": "(write-in)"}
RANK = re.compile(r"^rank(\d+)$", re.I)
DESIGN_COLUMNS = {"ballots": "n_ballots_cast", "with_marks": "n_ballots_with_marks", "overvotes": "n_overvotes",
                  "duplicates": "n_duplicate_marks", "writeins": "n_writeins"}


def totals(path: Path) -> dict[str, int]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        rows = list(reader)
    cols = [i for _, i in sorted((int(RANK.match(h).group(1)), i) for i, h in enumerate(header) if RANK.match(h))]
    if not cols:
        raise ValueError(f"{path.name}: no rank columns")
    out = dict.fromkeys(DESIGN_COLUMNS, 0)
    for n, row in enumerate(rows, start=2):
        if len(row) <= max(cols):
            raise ValueError(f"{path.name}: line {n} has {len(row)} cells, the header needs {max(cols) + 1}")
        marks = []
        for i in cols:
            key = re.sub(r"[\s\-_]", "", row[i]).lower()
            if key in TOKENS:
                if TOKENS[key] is not None:
                    marks.append(TOKENS[key])
            else:
                marks.append(row[i])  # a name: only its identity matters here
        out["ballots"] += 1
        out["with_marks"] += bool(marks)
        out["overvotes"] += marks.count("(overvote)")
        out["writeins"] += marks.count("(write-in)")
        out["duplicates"] += len(marks) - len(set(marks))
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Ballot totals of FairVote raw files against the design rows.")
    ap.add_argument("tables", nargs="*")
    ap.add_argument("--design", required=True, type=Path)
    ap.add_argument("--raw-dir", required=True, type=Path)
    ap.add_argument("--prefix", default="")
    ap.add_argument("--expect", action="append", default=[], metavar="TABLE=N", help="the total the city prints")
    args = ap.parse_args(argv)

    with open(args.design, newline="", encoding="utf-8") as f:
        design = {r["table"]: r for r in csv.DictReader(f)}
    city = {}
    for e in args.expect:
        t, _, n = e.partition("=")
        if not n.strip().isdigit():
            print(f"--expect {e!r}: use TABLE=N with N a whole number", file=sys.stderr)
            return 2
        city[t] = int(n)
    names = args.tables or sorted(t for t in design if args.prefix and t.startswith(args.prefix))
    missing = [t for t in [*names, *city] if t not in design]
    if not names or missing:
        print(f"no such design row: {missing or 'nothing selected, give table names or --prefix'}", file=sys.stderr)
        return 2

    bad = 0
    for t in names:
        try:
            got = totals(args.raw_dir / design[t]["source_file"])
        except (OSError, ValueError) as e:
            print(f"{t}: cannot read the raw file ({e})", file=sys.stderr)
            return 2
        diffs = [f"{k}: raw {got[k]}, design row {design[t][col]}" for k, col in DESIGN_COLUMNS.items()
                 if str(got[k]) != design[t][col]]
        if t in city and got["ballots"] != city[t]:
            diffs.append(f"ballots: raw {got['ballots']}, city {city[t]}")
        shown = ", ".join(f"{k} {v}" for k, v in got.items())
        print(f"{t}: {shown}; " + ("equal" if not diffs else "DIFFERENT"))
        for d in diffs:
            print(f"    {d}")
        bad += bool(diffs)
    print(f"{len(names) - bad}/{len(names)} equal")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
