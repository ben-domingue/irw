#!/usr/bin/env python3
"""Look up one or more IRW tables in the IRW Data Dictionary sheet.

This is the *only* place the skill looks up a table's paper/citation info --
per the brief, never fall back to searching the open web for a paper.  Reads
only the public CSV export of the dictionary sheet (gid=0), joining on
table.lower for case-insensitive matching.

Usage:
    python lookup_dictionary.py TABLE [TABLE ...]
    python lookup_dictionary.py --file tables.txt

Prints one JSON object per line (JSONL):
    {"table", "matched", "description", "url", "reference", "doi", "no_data"}

`no_data` is true when there was no dictionary match at all, or every one of
description/url/reference/doi came back empty. When `no_data` is true the
skill should stop for that table and stage a blank row with
Notes = "no working link" (the existing human-rater convention) -- don't try
to fetch or extract anything further for it.
"""
import argparse
import csv
import json

import requests

UA = {"User-Agent": "irw-auto-tag/1.0 (research; contact your-email)"}
DICT_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/export?format=csv&gid=0"
)


def load_dictionary():
    r = requests.get(DICT_SHEET_URL, headers=UA, timeout=30)
    r.raise_for_status()
    reader = csv.DictReader(r.text.splitlines())
    by_table = {}
    for row in reader:
        key = (row.get("table.lower") or row.get("table") or "").strip().lower()
        if key:
            by_table[key] = row
    return by_table


def lookup(table, by_table):
    row = by_table.get(table.strip().lower())
    if row is None:
        return {"table": table, "matched": False, "description": "", "url": "",
                 "reference": "", "doi": "", "no_data": True}
    description = (row.get("Description") or "").strip()
    url = (row.get("URL (for data)") or "").strip()
    reference = (row.get("Reference") or "").strip()
    doi = (row.get("DOI (for paper)") or "").strip()
    no_data = not any([description, url, reference, doi])
    return {"table": table, "matched": True, "description": description,
             "url": url, "reference": reference, "doi": doi, "no_data": no_data}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tables", nargs="*")
    ap.add_argument("--file", help="path to a file with one table name per line")
    args = ap.parse_args()

    tables = list(args.tables)
    if args.file:
        with open(args.file) as f:
            tables += [line.strip() for line in f if line.strip()]
    if not tables:
        ap.error("provide table name(s) or --file")

    by_table = load_dictionary()
    for t in tables:
        print(json.dumps(lookup(t, by_table)))


if __name__ == "__main__":
    main()
