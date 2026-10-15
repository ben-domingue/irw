"""Helpers shared by the non-FairVote rankings builders in this folder.

Not a package: each builder does `from rank_common import ...` and is run as a
file from anywhere (Python puts the script's own folder first on sys.path).
"""
from __future__ import annotations

import csv
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN = HERE / "design_tables.csv"
DESIGN_COLUMNS = ["table", "source_file", "collection", "jurisdiction", "date", "office", "method", "seats",
                  "n_positions", "n_candidates", "n_ballots_cast", "n_ballots_eligible_est", "n_ballots_with_marks",
                  "n_duplicate_marks", "n_overvotes", "n_writeins", "write_in_allowed", "candidate_order", "evidence"]


def fetch(url: str, dest: Path) -> Path:
    """Download `url` to `dest` once. The file is untrusted data: nothing in it is executed."""
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "irw-rankings-builder"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
            f.write(r.read())
    return dest


def code_candidates(names) -> dict[str, str]:
    """Alphabetical candidate codes (README, "Candidate codes"): distinct printed names sorted
    case-insensitively, c01.. with at least two digits (three from 100 candidates)."""
    distinct = sorted(set(names), key=lambda n: (n.casefold(), n))
    width = max(2, len(str(len(distinct))))
    return {n: f"c{i:0{width}d}" for i, n in enumerate(distinct, start=1)}


def write_table(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def upsert_design(record: dict) -> None:
    """Write or replace the table's row in design_tables.csv (same as eurovision_jurors.py)."""
    missing = [c for c in DESIGN_COLUMNS if c not in record]
    if missing:
        raise ValueError(f"design record missing {missing}")
    rows = []
    if DESIGN.exists():
        with open(DESIGN, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["table"] != record["table"]]
    rows.append({c: record[c] for c in DESIGN_COLUMNS})
    rows.sort(key=lambda r: r["table"])
    with open(DESIGN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=DESIGN_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def design_counts(rows: list[dict]) -> dict:
    """The counts the design record takes from the finished table."""
    ids = {r["id"] for r in rows}
    marks: dict[tuple, int] = {}
    for r in rows:
        k = (r["id"], r["task"], r["item"])
        marks[k] = marks.get(k, 0) + 1
    codes = {r["item"] for r in rows if r["item"] not in ("(write-in)", "(overvote)")}
    return {"n_positions": max(int(r["resp"]) for r in rows), "n_candidates": len(codes),
            "n_ballots_with_marks": len(ids),
            "n_duplicate_marks": sum(v - 1 for v in marks.values() if v > 1),
            "n_overvotes": sum(1 for r in rows if r["item"] == "(overvote)"),
            "n_writeins": sum(1 for r in rows if r["item"] == "(write-in)")}
