#!/usr/bin/env python3
"""Re-derive controlled-vocabulary values by enumerating actual non-empty
cell values in the live "IRW Tags" sheet.

There is no Sheets API / OAuth credential available to this skill (confirmed:
Google Drive tools 404 on both sheet IDs -- they're not shared with the
connected account -- and only the public CSV export is reachable), so the
sheet's real data-validation dropdown rules can't be read directly. This
enumerates every value that has actually been *entered* instead, which is a
strong proxy: as of the 2026-07-27 run these columns had zero stray/off-list
values across ~1960 rows, consistent with enforced dropdown validation.

Re-run this whenever you suspect the sheet's dropdowns have changed (a new
option added, e.g.) -- references/vocab.md is hand-maintained and won't
update itself; diff this output against it.

NOTE (2026-08-29, issue #1720): "Sample" and "Construct type" are no longer
governed by this script alone. TAG_VOCAB in metadata/tag_normalize.R is now the
authoritative list for those two columns, and 03_tags.R stops the pipeline on
any atom outside it. If this script reports a value those lists don't have,
that is a real finding -- reconcile them rather than editing vocab.md alone.
Also note this script reads the SHEET, which still holds
"Internet-based (Mturkers, etc)"; the export renames it to "Internet-based".

Usage: python derive_vocab.py
"""
import csv

import requests

UA = {"User-Agent": "irw-auto-tag/1.0 (research; contact your-email)"}
TAGS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/export?format=csv&gid=126134123"
)

SINGLE_SELECT = ["Age Range", "Item format", "Item text available?"]
# comma-separated multi-select; one option ("Internet-based (Mturkers, etc)")
# contains a literal comma, so a naive split() breaks it -- protect it first.
# Confirmed multi-select empirically (2026-07-27 run): "Child Age" and
# "Measurement tool" both have rows with >1 comma-separated value, even
# though they read as single-select at a glance.
MULTI_SELECT = ["Sample", "Construct type", "Child Age (for child-focused studies)",
                "Measurement tool"]
KNOWN_COMMA_TOKENS = ["Internet-based (Mturkers, etc)"]


def split_multi(cell):
    tmp = cell
    for i, tok in enumerate(KNOWN_COMMA_TOKENS):
        tmp = tmp.replace(tok, f"\x00{i}\x00")
    parts = [p.strip() for p in tmp.split(",")]
    restored = []
    for p in parts:
        for i, tok in enumerate(KNOWN_COMMA_TOKENS):
            p = p.replace(f"\x00{i}\x00", tok)
        # a handful of rows have the option typed with literal quote marks
        # around it (e.g. pasted from a CSV) -- normalize those away
        p = p.strip().strip('"').strip()
        if p:
            restored.append(p)
    return restored


def main():
    r = requests.get(TAGS_SHEET_URL, headers=UA, timeout=30)
    r.raise_for_status()
    rows = list(csv.DictReader(r.text.splitlines()))[1:]  # drop instruction row

    for col in SINGLE_SELECT:
        vals = sorted({(row.get(col) or "").strip() for row in rows if (row.get(col) or "").strip()})
        print(f"\n{col} ({len(vals)}):")
        for v in vals:
            print(f"  - {v}")

    for col in MULTI_SELECT:
        vals = set()
        for row in rows:
            cell = (row.get(col) or "").strip()
            if cell:
                vals.update(split_multi(cell))
        print(f"\n{col} ({len(vals)}):")
        for v in sorted(vals):
            print(f"  - {v}")


if __name__ == "__main__":
    main()
