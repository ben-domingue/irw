#!/usr/bin/env python3
"""Look up one or more IRW tables in the published IRW Data Dictionary.

This is the *only* place the skill looks up a table's paper/citation info --
per the brief, never fall back to searching the open web for a paper.

Reads the PUBLISHED record first -- `metadata/*biblio*.csv`, the export users
see -- not the dictionary sheet (#2067). The export carries corrections the
sheet deliberately never receives: five wrong Descriptions fixed by
`DESCRIPTION_OVERRIDES` (one sheet row still calls a chronic-diagnosis
checklist "PROMIS fatigue", and the tagger tagged from it), licence fixes, and
`dictionary_auto.csv` rows that reach the export without reaching the sheet
(210 tables on 2026-09-27; 339 exported tables had no sheet row at all).

A table the weekly export has not reached yet -- ingested since Monday -- falls
back to its `dictionary_auto.csv` row, then to the sheet's public CSV export,
so a new table is never reported `no_data` merely for being new (that would
stage a "no working link" sentinel and stop the tagger ever retrying it).
`source` says which one answered. Matching is case-insensitive throughout.

Usage:
    python lookup_dictionary.py TABLE [TABLE ...]
    python lookup_dictionary.py --file tables.txt

Prints one JSON object per line (JSONL):
    {"table", "matched", "description", "url", "reference", "doi", "data_doi",
     "no_data", "source"}

`doi` is the PAPER's DOI and is empty when the dictionary's one DOI column
holds a data-repository DOI instead -- that value comes back as `data_doi`
(#1690). Do not resolve a `data_doi` expecting an article: it resolves to the
deposit, whose creators are the depositor and whose year is the deposit year.

`no_data` is true when there was no dictionary match at all, or every one of
description/url/reference/doi came back empty. When `no_data` is true the
skill should stop for that table and stage a blank row with
Notes = "no working link" (the existing human-rater convention) -- don't try
to fetch or extract anything further for it.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import requests

UA = {"User-Agent": "irw-auto-tag/1.0 (research; contact your-email)"}
DICT_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/export?format=csv&gid=0"
)


def load_dictionary():
    """The sheet's public CSV export, keyed on table.lower. The last resort."""
    r = requests.get(DICT_SHEET_URL, headers=UA, timeout=30)
    r.raise_for_status()
    reader = csv.DictReader(r.text.splitlines())
    by_table = {}
    for row in reader:
        key = (row.get("table.lower") or row.get("table") or "").strip().lower()
        if key:
            by_table[key] = row
    return by_table


##The DOI rule lives in one place (#1690); this reaches it by path because the
##skill's scripts are not on a shared import path.
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "automated_finding"))
from doi_hygiene import classify, normalize  # noqa: E402
from published_dictionary import load_auto_rows, load_published  # noqa: E402


def split_doi(value):
    """(paper DOI, data DOI) from the sheet's one overloaded column (#1690).

    979 dictionary rows hold a data-repository DOI here. biblio.csv has the
    export-time split already (metadata/dict_union.R), but the fallback rows
    below come from the sheet's layout -- and handing a Dataverse DOI back as
    `doi` is the exact
    failure #1764 documented: the fetch succeeds, the content verifies as a
    genuine record, and the table is tagged from the wrong document. Reported
    under its own key so a caller has to decide to use it.
    """
    doi = normalize(value)[0]
    if classify(doi) == "data_doi":
        return "", doi
    return doi, ""


def _from_published(rec):
    """A biblio.csv record in lookup()'s shape. The export has already split
    paper from data DOIs; split_doi still runs, so a data DOI left in the paper
    column can never come back as `doi`."""
    doi, stray = split_doi(rec["doi"])
    data_doi = normalize(rec["data_doi"])[0] if rec["data_doi"] else stray
    return {"description": rec["description"], "url": rec["url"],
            "reference": rec["reference"], "doi": doi, "data_doi": data_doi or ""}


def _from_sheet_row(row):
    """A row in the sheet's column names (the sheet itself, or dictionary_auto)."""
    doi, data_doi = split_doi(row.get("DOI (for paper)"))
    if not data_doi and (row.get("DOI (for data)") or "").strip():
        data_doi = normalize(row.get("DOI (for data)"))[0] or ""
    return {"description": (row.get("Description") or "").strip(),
            "url": (row.get("URL (for data)") or "").strip(),
            "reference": (row.get("Reference") or "").strip(),
            "doi": doi, "data_doi": data_doi}


def lookup(table, published, auto=None, sheet=None):
    """Published record first, then dictionary_auto, then the sheet.

    `sheet` may be a callable returning the sheet mapping, so the network is
    only touched when the local record has no row for the table.
    """
    key = table.strip().lower()
    if key in published:
        vals, source = _from_published(published[key]), published[key]["file"]
    elif auto and key in auto:
        vals, source = _from_sheet_row(auto[key]), "automated_finding/dictionary_auto.csv"
    else:
        by_table = sheet() if callable(sheet) else (sheet or {})
        row = by_table.get(key)
        if row is None:
            return {"table": table, "matched": False, "description": "", "url": "",
                    "reference": "", "doi": "", "data_doi": "", "no_data": True,
                    "source": ""}
        vals, source = _from_sheet_row(row), "sheet"
    no_data = not any(vals.values())
    return {"table": table, "matched": True, **vals, "no_data": no_data,
            "source": source}


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

    published, auto = load_published(), load_auto_rows()
    cache = {}

    def sheet():
        if "rows" not in cache:
            cache["rows"] = load_dictionary()
        return cache["rows"]

    for t in tables:
        print(json.dumps(lookup(t, published, auto, sheet)))


if __name__ == "__main__":
    main()
