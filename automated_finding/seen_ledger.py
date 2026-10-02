"""The connectors' cross-run "seen" ledgers, with the verdict on each row.

pmc_seen_dois.csv, plos_seen_dois.csv and repo_triage_seen_keys.csv stop a
candidate from being downloaded and triaged twice. Until 2026-09-30 they held
only the key and a date, so a heuristic verdict such as `no_usable_file` --
wrong for 5 of a random 20 PMC rejects before the Data Availability fix --
retired a candidate forever with nothing recording why (irw#2222).

Each row now also carries the run's `flag`. Runs still skip every key in the
ledger, so nothing is re-downloaded, but an exclusion is reversible: when a
resolver improves, `drop` the rows carrying the flag it fixes and the next run
re-triages them.

    python seen_ledger.py drop pmc_seen_dois.csv --flag no_usable_file
    python seen_ledger.py drop pmc_seen_dois.csv --flag no_usable_file --before 2026-09-23 --apply

Rows written before the column existed have a blank flag, except where a
run's output CSV still recorded the verdict (backfilled 2026-09-30).
"""
from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone


def _rewrite(path: str, fieldnames: list, rows: list) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def _read(path: str) -> tuple[list, list]:
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def append_seen(path: str, key_field: str, items) -> None:
    """Append `items` -- each a key, or a (key, flag) pair -- dated today.

    A ledger whose header predates the `flag` column is upgraded in place
    first (existing rows get a blank flag), so an old checkout's file and a
    new one never mix two- and three-field rows under one header."""
    rows = []
    for it in items:
        key, flag = (it, "") if isinstance(it, str) else it
        rows.append((key, flag or ""))
    if not rows:
        return
    fieldnames = [key_field, "date", "flag"]
    if os.path.exists(path):
        header, existing = _read(path)
        if "flag" not in header:
            _rewrite(path, fieldnames,
                     [{key_field: r.get(key_field, ""), "date": r.get("date", ""), "flag": ""}
                      for r in existing])
    file_exists = os.path.exists(path)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerows({key_field: k, "date": today, "flag": fl} for k, fl in rows)


def drop(path: str, flag: str, before: str | None = None, apply: bool = False) -> int:
    """Remove rows carrying `flag` (dated before `before`, if given) so the
    next run re-triages them. Dry run unless `apply`."""
    header, rows = _read(path)
    if "flag" not in header:
        raise SystemExit(f"{path} has no flag column; nothing can be selected by verdict")
    hit = [r for r in rows
           if r.get("flag") == flag and (before is None or (r.get("date") or "") < before)]
    print(f"{path}: {len(hit)} of {len(rows)} row(s) carry flag={flag!r}"
          + (f" dated before {before}" if before else ""))
    if apply and hit:
        hit_ids = {id(r) for r in hit}
        _rewrite(path, header, [r for r in rows if id(r) not in hit_ids])
        print(f"removed {len(hit)}; the next run re-triages them")
    elif hit:
        print("dry run -- pass --apply to remove them")
    return len(hit)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("drop", help="remove rows by verdict so they are re-triaged")
    d.add_argument("path")
    d.add_argument("--flag", required=True)
    d.add_argument("--before", help="only rows dated before this YYYY-MM-DD")
    d.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.cmd == "drop":
        drop(a.path, a.flag, a.before, a.apply)


if __name__ == "__main__":
    main()
