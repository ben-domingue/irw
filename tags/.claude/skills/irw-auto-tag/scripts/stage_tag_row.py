#!/usr/bin/env python3
"""Append one extracted tag row to the local staging CSV.

Never writes to the Google Sheet directly -- there is no write-capable tool
wired up for it (confirmed: only the public CSV export is reachable; no
googlesheets4/service-account credentials exist in this repo). This mirrors
automated_finding's established pattern: stage rows in a repo-tracked CSV
(tags/tags_auto.csv, NOT scratchpad or /tmp -- a scratchpad path can't be
found again once the session ends) rather than claiming the sheet was
updated.

Since issue #1723 that file is a real pipeline input: metadata/03_tags.R
unions it into tags.csv on every run, human rows in the Sheet winning on
conflict. So rows written here reach the published table via a merged PR,
with no paste step. Rater is forced to "claude-auto" below because
03_tags.R refuses to run on a file containing any other rater.

Refuses to add a table that's already in the staging file (local
idempotency) unless --force is passed. This does NOT check the live sheet --
run check_table_status.py first for that.

Usage: pass one row as JSON on stdin, e.g.:
    echo '{"table": "foo_2024", "construct_name": "..."}' | python stage_tag_row.py
    echo '{...}' | python stage_tag_row.py --force

JSON keys (all optional except "table"): table, construct_name, context_text,
item_text_available, age_range, child_age, sample, construct_type,
measurement_tool, item_format, primary_languages, notes
"""
import csv
import json
import sys
from pathlib import Path

# scripts/ -> irw-auto-tag/ -> skills/ -> .claude/ -> tags/
STAGING_PATH = Path(__file__).resolve().parents[4] / "tags_auto.csv"

COLUMNS = [
    "table", "Rater", "Construct Name", "Context Text", "Item text available?",
    "Age Range", "Child Age (for child-focused studies)", "Sample",
    "Construct type", "Measurement tool", "Item format", "Primary Language(s)",
    "Notes",
]

KEY_MAP = {
    "table": "table",
    "construct_name": "Construct Name",
    "context_text": "Context Text",
    "item_text_available": "Item text available?",
    "age_range": "Age Range",
    "child_age": "Child Age (for child-focused studies)",
    "sample": "Sample",
    "construct_type": "Construct type",
    "measurement_tool": "Measurement tool",
    "item_format": "Item format",
    "primary_languages": "Primary Language(s)",
    "notes": "Notes",
}


def main():
    force = "--force" in sys.argv
    payload = json.load(sys.stdin)
    if not payload.get("table"):
        sys.exit("payload needs a non-empty 'table'")

    row = {c: "" for c in COLUMNS}
    for k, v in payload.items():
        col = KEY_MAP.get(k)
        if col is None:
            sys.exit(f"unknown field: {k}")
        row[col] = v if v is not None else ""
    row["Rater"] = "claude-auto"

    existing = set()
    file_exists = STAGING_PATH.exists()
    if file_exists:
        with open(STAGING_PATH, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                existing.add((r.get("table") or "").strip().lower())

    if row["table"].strip().lower() in existing and not force:
        sys.exit(f"{row['table']} is already in {STAGING_PATH} -- use --force to add a duplicate row")

    with open(STAGING_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"staged {row['table']} -> {STAGING_PATH}")


if __name__ == "__main__":
    main()
