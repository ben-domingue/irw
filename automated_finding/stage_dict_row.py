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
--force (add a second row) or --replace (swap the existing row for this one, in
place) is passed. --replace refuses a table that is not in the file, so a typo
cannot quietly add a row, and it rewrites only that table's lines: every other
row stays byte-for-byte as it was, whatever quoting it was written with. This does NOT check the live sheet -- a table the humans
already described is not an error, the union will simply let their cells win.

Usage: pass one row as JSON on stdin, e.g.:
    echo '{"table": "foo_2024", "description": "...", "derived_license": "CC BY 4.0"}' \\
        | python stage_dict_row.py

For a comps, nominal, simsyn or conjoint table add `--source comps|nom|sim|conj`; each
dictionary has its own automated file (#2628). Default is core.

`codebook_url` (#2770): the source's own codebook FILE -- whoever builds a
table has just read it to write the script. Give its URL, or "none" when the
source ships no codebook; never a guess, and never the deposit's landing page
(that is already `url`). It is not a dictionary column: it is written to
codebook_at_ingest.csv beside this file, which metadata/find_codebook_links.py
reads as its strongest evidence (`how_found = recorded_at_ingest`). Restaging
a table replaces its codebook row.
"""
import csv
import io
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

##One automated file per dictionary sheet, matching the `dbs` list in
##metadata/02_biblio.R (#2628). Same header, same refusals; only the file
##differs. `core` stays the default so existing callers are unchanged.
SOURCE_FILES = {
    "core": "dictionary_auto.csv",
    "comps": "dictionary_auto_comps.csv",
    "nom": "dictionary_auto_nom.csv",
    "sim": "dictionary_auto_sim.csv",
    ##Conjoint experiments (irw_conjoint). Staged here before the source is
    ##registered; metadata/02_biblio.R does not read this file yet.
    "conj": "dictionary_auto_conj.csv",
}


##The source's own codebook file, recorded when the table is built (#2770). One
##row per table; restaging replaces it. Not part of the dictionary union.
CODEBOOK_PATH = Path(os.environ.get("IRW_CODEBOOK_INGEST_PATH")
                     or Path(__file__).resolve().parent / "codebook_at_ingest.csv")
CODEBOOK_COLUMNS = ["table", "source", "codebook_url", "recorded_at"]


def record_codebook(table, source, url):
    """Upsert `table`'s codebook row. `url` is already validated."""
    from datetime import date
    rows = []
    if CODEBOOK_PATH.exists():
        with open(CODEBOOK_PATH, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f)
                    if (r.get("table") or "").strip().lower() != table.lower()]
    rows.append({"table": table, "source": source, "codebook_url": url,
                 "recorded_at": date.today().isoformat()})
    rows.sort(key=lambda r: r["table"].lower())
    with open(CODEBOOK_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CODEBOOK_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def staging_path(source):
    """The file a row for `source` is staged to. IRW_DICT_AUTO_PATH wins, so the
    tests can point any source at a scratch file."""
    if source not in SOURCE_FILES:
        sys.exit(f"unknown --source {source!r} (known: {', '.join(SOURCE_FILES)})")
    if os.environ.get("IRW_DICT_AUTO_PATH"):
        return Path(os.environ["IRW_DICT_AUTO_PATH"])
    return Path(__file__).resolve().parent / SOURCE_FILES[source]

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
    "Source via",
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
    "source_via": "Source via",
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


def _raw_records(raw):
    """Split CSV text into its records, each the exact text it was written as.

    A record ends at a newline outside quotes, i.e. once its count of '"' is
    even (RFC 4180 escapes a quote by doubling it, so parity is exact).
    """
    out, cur = [], ""
    for line in raw.splitlines(keepends=True):
        cur += line
        if cur.count('"') % 2 == 0:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def replace_row(path, row):
    """Swap the record(s) for row's table for one new record, in place."""
    with open(path, newline="", encoding="utf-8") as f:
        raw = f.read()
    records = _raw_records(raw)
    new = io.StringIO(newline="")
    csv.DictWriter(new, fieldnames=COLUMNS, lineterminator="\n").writerow(row)
    out, placed = [records[0]], False
    for rec in records[1:]:
        fields = next(csv.reader(io.StringIO(rec, newline="")), [""])
        if fields and fields[0].strip().lower() == row["table.lower"]:
            if not placed:
                out.append(new.getvalue())
                placed = True
            continue
        out.append(rec)
    if not placed:
        sys.exit(f"{row['table']} is not in {path} -- --replace only swaps an existing row")
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("".join(out))


def main():
    force = "--force" in sys.argv
    replace = "--replace" in sys.argv
    if force and replace:
        sys.exit("--force adds a duplicate row and --replace swaps the existing one; pass one")

    # Check for --source-via flag if passed via CLI args
    cli_source_via = None
    source = "core"
    for i, arg in enumerate(sys.argv):
        if arg == "--source-via" and i + 1 < len(sys.argv):
            cli_source_via = sys.argv[i + 1]
        elif arg.startswith("--source-via="):
            cli_source_via = arg.split("=", 1)[1]
        elif arg == "--source" and i + 1 < len(sys.argv):
            source = sys.argv[i + 1]
        elif arg.startswith("--source="):
            source = arg.split("=", 1)[1]
    path = staging_path(source)

    payload = json.load(sys.stdin)

    # CLI flag overrides or defaults payload if provided
    if cli_source_via is not None:
        payload["source_via"] = cli_source_via

    ##Not a dictionary column (#2770): validated here, written after the row.
    codebook = clean(payload.pop("codebook_url", None))
    if codebook and codebook.lower() != "none" and not re.match(r"^https?://\S+$", codebook):
        sys.exit(f"'codebook_url' must be the codebook file's URL or \"none\": {codebook!r}")
    if codebook.lower() == "none":
        codebook = "none"

    row = {c: "" for c in COLUMNS}
    for key, value in payload.items():
        col = KEY_MAP.get(key)
        if col is None:
            sys.exit(f"unknown field: {key} (known: {', '.join(sorted(KEY_MAP) + ['codebook_url'])})")
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
    file_exists = path.exists()
    if file_exists:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ##Appending a wider row under a narrower header writes every value
            ##after the new columns under the wrong name, and nothing complains.
            ##Refuse instead: append-only is right for the DATA, the SCHEMA gets
            ##migrated deliberately.
            if reader.fieldnames != COLUMNS:
                sys.exit(
                    f"{path} has a {len(reader.fieldnames or [])}-column "
                    f"header and this script writes {len(COLUMNS)}. Migrate the "
                    f"file first -- appending would silently shift every value.\n"
                    f"  found:    {reader.fieldnames}\n  expected: {COLUMNS}")
            for r in reader:
                existing.add((r.get("table") or "").strip().lower())

    if replace:
        if not file_exists:
            sys.exit(f"{path} does not exist -- --replace only swaps an existing row")
        replace_row(path, row)
        print(f"replaced {row['table']} in {path}")
        if codebook:
            record_codebook(row["table"], source, codebook)
            print(f"recorded codebook for {row['table']} -> {CODEBOOK_PATH}")
        return

    if row["table.lower"] in existing and not force:
        sys.exit(f"{row['table']} is already in {path} "
                 f"-- use --replace to swap it, or --force to add a duplicate row")

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"staged {row['table']} -> {path}")
    if codebook:
        record_codebook(row["table"], source, codebook)
        print(f"recorded codebook for {row['table']} -> {CODEBOOK_PATH}")


if __name__ == "__main__":
    main()
