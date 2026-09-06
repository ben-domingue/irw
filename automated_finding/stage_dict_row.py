#!/usr/bin/env python3
"""Append one dictionary row to the local staging CSV.

Replaces the per-batch `make_biblio_*.py` scripts and the File > Import >
Append procedure they fed. Those emitted a CSV shaped for a human to paste into
the Data Dictionary sheet; ~200 rows landed that way in a single day with no
diff, no blame and no revert (issue #1732, roadmap item 6b).

Never writes to the Google Sheet directly -- there is no service account and
there is not going to be one (#1708, recorded in ARCHITECTURE.md section 3).
Since #1732 this file is a real pipeline input: metadata/02_biblio.R unions it
into the sheet export on every run, COLUMN-WISE, with the human winning every
cell they filled. So rows written here reach biblio.csv through a merged PR,
with no paste step.

The paste path's whole fragility surface is handled here instead of by a
procedure someone has to remember:

  * quoting -- csv writes RFC4180, so a comma or newline in Description no
    longer shifts every later column left
  * the leading =, +, -, @ that Sheets interprets as a formula
  * `Public Reshare?`, which 02_biblio.R uses to drop non-public rows. A blank
    one used to mean the row silently never reached biblio; it is refused here
  * `Contributor`, forced to "automated" below, because 02_biblio.R refuses to
    run on a file containing any other contributor

Refuses to add a table already in the staging file (local idempotency) unless
--force is passed. This does NOT check the live sheet -- a table the humans
already described is not an error, the union will simply let their cells win.

Usage: pass one row as JSON on stdin, e.g.:
    echo '{"table": "foo_2024", "description": "...", "derived_license": "CC BY 4.0"}' \\
        | python stage_dict_row.py
"""
import csv
import json
import os
import sys
from pathlib import Path

##IRW_DICT_AUTO_PATH exists so metadata/tests/manual_dict_test.R can exercise
##this writer for real -- same quoting, same refusals -- against a scratch file
##instead of the tracked one. Production never sets it.
STAGING_PATH = Path(os.environ.get("IRW_DICT_AUTO_PATH")
                    or Path(__file__).resolve().parent / "dictionary_auto.csv")

##Must stay identical to DICT_AUTO_COLS in metadata/dict_union.R, which refuses
##to merge a file whose header does not match exactly.
##
##The two custom-licence columns are named distinctly here even though the sheet
##names both of them "Custom License" (positions 8 and 11). That duplicate is
##what made a name-keyed union ambiguous; resolve_dict_cols() in dict_union.R
##maps these two onto whichever names the sheet is currently using. Do not
##"simplify" them back to one name.
COLUMNS = [
    "table", "table.lower", "Description", "URL (for data)", "Reference",
    "DOI (for paper)", "Original License", "Custom License (source)",
    "Public Reshare?", "Derived License", "Custom License (derived)",
    "Notes", "Contributor", "Date",
]

CONTRIBUTOR = "automated"

KEY_MAP = {
    "table": "table",
    "description": "Description",
    "url": "URL (for data)",
    "reference": "Reference",
    "doi": "DOI (for paper)",
    "original_license": "Original License",
    "custom_license_source": "Custom License (source)",
    "public_reshare": "Public Reshare?",
    "derived_license": "Derived License",
    "custom_license_derived": "Custom License (derived)",
    "notes": "Notes",
    "date": "Date",
}

def clean(value):
    """One cell, normalised but never rewritten.

    Deliberately does NOT escape a leading "=", "+", "-" or "@". That was a
    paste-path mitigation -- Sheets reads those as a formula -- and this file
    is never pasted into Sheets: 02_biblio.R reads it directly. Prefixing an
    apostrophe here corrupts the value instead of protecting it. Caught by
    tests/manual_dict_test.R replaying the 7/13/2026 batch, where two Notes
    cells legitimately begin "-1 sentinel values ..." and came back as
    "\'-1 sentinel values ...".

    If someone ever does want to import this file into Sheets by hand, escape
    it at that point. Do not reintroduce it here.
    """
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()


def main():
    force = "--force" in sys.argv
    payload = json.load(sys.stdin)

    row = {c: "" for c in COLUMNS}
    for key, value in payload.items():
        col = KEY_MAP.get(key)
        if col is None:
            sys.exit(f"unknown field: {key} (known: {', '.join(sorted(KEY_MAP))})")
        row[col] = clean(value)

    if not row["table"]:
        sys.exit("payload needs a non-empty 'table'")
    ##Derived, never accepted from the payload: every downstream join is on the
    ##lowercased name, and letting a caller supply a mismatched one would make a
    ##row that silently matches nothing.
    row["table.lower"] = row["table"].lower()
    row["Contributor"] = CONTRIBUTOR

    ##02_biblio.R drops every non-Public row before biblio is built. A blank
    ##here is not a small omission -- the row vanishes with no error and no
    ##diff, which is precisely the failure this whole change exists to end.
    if not row["Public Reshare?"]:
        sys.exit("'public_reshare' is required (e.g. \"Public\" or \"Private\"); "
                 "02_biblio.R silently drops rows that leave it blank")
    ##A public row with no licence cannot be published, and finding that out at
    ##export time means finding it out for a whole batch at once.
    if row["Public Reshare?"] == "Public" and not row["Derived License"]:
        sys.exit("a Public row needs a 'derived_license' (e.g. \"CC BY 4.0\")")

    existing = set()
    file_exists = STAGING_PATH.exists()
    if file_exists:
        with open(STAGING_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ##Appending a wider row under a narrower header writes every value
            ##after the new columns under the wrong name, and nothing complains.
            ##Refuse instead: append-only is right for the DATA, the SCHEMA gets
            ##migrated deliberately.
            if reader.fieldnames != COLUMNS:
                sys.exit(
                    f"{STAGING_PATH} has a {len(reader.fieldnames or [])}-column "
                    f"header and this script writes {len(COLUMNS)}. Migrate the "
                    f"file first -- appending would silently shift every value.\n"
                    f"  found:    {reader.fieldnames}\n  expected: {COLUMNS}")
            for r in reader:
                existing.add((r.get("table") or "").strip().lower())

    if row["table.lower"] in existing and not force:
        sys.exit(f"{row['table']} is already in {STAGING_PATH} "
                 f"-- use --force to add a duplicate row")

    with open(STAGING_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"staged {row['table']} -> {STAGING_PATH}")


if __name__ == "__main__":
    main()
