#!/usr/bin/env python3
"""Check whether IRW tables already have a row in the "IRW Tags" sheet.

Idempotency gate: run before staging a new tag row for a table, and before
re-tagging, so the skill never silently duplicates or overwrites a human
rater's work. Reads only the public CSV export of the tags sheet -- no
credentials needed.

Usage:
    python check_table_status.py TABLE [TABLE ...]

Prints one JSON object per line: {"table": ..., "tagged": bool, "rater": str|null}
"""
import argparse
import csv
import json

import requests

UA = {"User-Agent": "irw-auto-tag/1.0 (research; contact your-email)"}
TAGS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/export?format=csv&gid=126134123"
)


def load_tagged():
    r = requests.get(TAGS_SHEET_URL, headers=UA, timeout=30)
    r.raise_for_status()
    rows = list(csv.DictReader(r.text.splitlines()))
    # first data row is the sheet's own instruction/template row, not a real table
    rows = rows[1:]
    by_table = {}
    for row in rows:
        key = (row.get("table") or "").strip().lower()
        if key:
            by_table[key] = row.get("Rater", "")
    return by_table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tables", nargs="+")
    args = ap.parse_args()

    by_table = load_tagged()
    for t in args.tables:
        rater = by_table.get(t.strip().lower())
        print(json.dumps({"table": t, "tagged": rater is not None, "rater": rater}))


if __name__ == "__main__":
    main()
