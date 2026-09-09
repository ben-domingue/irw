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
import re
import sys
from pathlib import Path

from doi_hygiene import classify, normalize

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
##`DOI (for data)` has no counterpart in the sheet: it is the #1690 split, and
##it lives only here and in the merged export. See DICT_AUTO_ONLY_COLS in
##metadata/dict_union.R.
##Kept identical to DICT_NAME_RE in metadata/dict_union.R -- see the comment
##there for why the pattern is this wide (307 non-lowercase names, and some rows
##still carry a trailing ".csv").
NAME_OK_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,80}$")

COLUMNS = [
    "table", "table.lower", "Description", "URL (for data)", "Reference",
    "DOI (for paper)", "DOI (for data)", "Original License",
    "Custom License (source)", "Public Reshare?", "Derived License",
    "Custom License (derived)", "Notes", "Contributor", "Date",
]

CONTRIBUTOR = "automated"

KEY_MAP = {
    "table": "table",
    "description": "Description",
    "url": "URL (for data)",
    "reference": "Reference",
    "doi": "DOI (for paper)",
    "doi_data": "DOI (for data)",
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
    ##A `table` cell that is not a table name is a wrong-column paste, and
    ##nothing downstream notices: dict_key() in dict_union.R is tolower(trimws())
    ##and will happily key a row on a sentence. One such cell reached biblio.csv
    ##on main and asserted a licence and a DOI for a table that does not exist
    ##(#2079). This writer is interactive, so a bad name here is always a
    ##mistake -- fail loudly rather than report. Mirrored by DICT_NAME_RE in
    ##metadata/dict_union.R, which reports instead, because the sheet is a human
    ##surface and a pipeline run must not stop on it.
    if not NAME_OK_RE.match(row["table"]):
        sys.exit(f"'table' is not a table name: {row['table']!r}. Expected "
                 f"{NAME_OK_RE.pattern} -- a citation or description belongs in "
                 f"'reference' or 'description', not here.")

    ##`DOI (for paper)` acquired 83 cells wrapped in a resolver URL, prefixed
    ##`data doi: `, or carrying a journal supplement suffix before anyone
    ##looked (#1690). Those forms are mechanically removable and mean the same
    ##thing afterwards, so they are removed here rather than reported. What is
    ##NOT touched is a data-repository DOI: replacing it needs the linked
    ##publication, which is the open schema question on #1690, so the row is
    ##written as given and the cell is left for that decision.
    if row["DOI (for data)"]:
        row["DOI (for data)"] = normalize(row["DOI (for data)"])[0]
    if row["DOI (for paper)"]:
        doi, rules = normalize(row["DOI (for paper)"])
        if rules:
            print(f"note: DOI normalised ({', '.join(rules)}): "
                  f"{row['DOI (for paper)']!r} -> {doi!r}", file=sys.stderr)
        row["DOI (for paper)"] = doi
        kind = classify(doi)
        ##A deposit DOI is not a paper DOI, and putting one here is the defect
        ###1690 exists for. It is not ambiguous -- a Dataverse or figshare
        ##prefix says what the object is -- so route it rather than refuse it,
        ##and say so. A caller that knows better passes `doi_data` directly.
        if kind == "data_doi" and not row["DOI (for data)"]:
            print(f"note: {doi} is a data-repository DOI; filed under "
                  f"'DOI (for data)', not 'DOI (for paper)' (#1690)",
                  file=sys.stderr)
            row["DOI (for data)"] = doi
            row["DOI (for paper)"] = ""
            doi, kind = "", "empty"
        ##Free text ("not yet published", a landing-page URL) is not a DOI and
        ##never becomes one downstream -- it just fails to resolve, quietly, in
        ##whatever tries next. Refuse it at the door; leave the cell blank and
        ##put the sentence in `notes` instead.
        if kind == "free_text":
            sys.exit(f"'doi' is not a DOI: {doi!r}. Leave it blank and put the "
                     f"explanation in 'notes'.")
        if kind == "multiple":
            sys.exit(f"'doi' holds more than one DOI: {doi!r}. One row, one "
                     f"paper DOI; the others belong in 'notes'.")
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
