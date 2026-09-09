#!/usr/bin/env python3
"""One-off: move every deposit DOI out of `DOI (for paper)` (#1690).

979 dictionary rows hold a data-repository DOI (Dataverse, Mendeley, figshare,
Zenodo, Dryad, OSF, ICPSR) in a column that means "the paper". Ben's ruling on
2026-09-06 was to split the two columns WITHOUT touching the Google Sheet, so
the new `DOI (for data)` column lives only in dictionary_auto.csv and in the
merged export. This writes those rows.

What the union then does with them, in metadata/dict_union.R:

  * `DOI (for data)` is an auto-only column: the sheet never has it, and
    union_dict() creates it in the merged frame.
  * where a row's automated `DOI (for data)` equals the value the sheet holds in
    `DOI (for paper)`, the paper cell is cleared IN THE EXPORT. That is the one
    exception to "a human cell wins the cell it occupies", and the equality test
    is what keeps it narrow.

So this script must write the deposit DOI EXACTLY as the sheet holds it, modulo
doi_hygiene.normalize(). If the two ever disagree the override silently never
fires and the corpus keeps citing deposits as papers, which is the failure this
whole change is for -- hence --verify, which re-reads the sheet and reports any
row whose value would not match.

`Public Reshare?` and `Derived License` are copied from the sheet rather than
invented: read_dict_auto() refuses a blank reshare (02_biblio.R drops non-Public
rows silently), and the union will not overwrite either cell because the human
already filled it. A row whose sheet reshare is blank is skipped and reported --
it has a bigger problem than its DOI.

    python3 backfill_data_dois.py --dry-run
    python3 backfill_data_dois.py            ##rewrites dictionary_auto.csv
    python3 backfill_data_dois.py --verify   ##re-check against the live sheet
"""
import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from doi_hygiene import DOI_COL, classify, load_rows, normalize  # noqa: E402
from stage_dict_row import CONTRIBUTOR, COLUMNS, STAGING_PATH  # noqa: E402

DATA_COL = "DOI (for data)"


##A row this script wrote: a deposit DOI and the two cells needed to get it past
##read_dict_auto()'s guards, and nothing else. Distinguishing it from a real
##staged row is what makes a re-run idempotent.
BACKFILL_CONTENT_COLS = ("table", "table.lower", DATA_COL, "Public Reshare?",
                         "Derived License", "Contributor", "Date")


def is_backfill_row(row):
    if not (row.get(DATA_COL) or "").strip():
        return False
    return not any((row.get(c) or "").strip()
                   for c in row if c not in BACKFILL_CONTENT_COLS)


def backfill_rows(dict_rows):
    """The rows to write, plus the rows that had to be skipped."""
    out, skipped = [], []
    for r in dict_rows:
        doi = normalize(r.get(DOI_COL, ""))[0]
        if classify(doi) != "data_doi":
            continue
        table = (r.get("table") or "").strip()
        reshare = (r.get("Public Reshare?") or "").strip()
        if not table:
            continue
        if not reshare:
            skipped.append((table, "blank `Public Reshare?` in the sheet"))
            continue
        row = {c: "" for c in COLUMNS}
        row["table"] = table
        row["table.lower"] = table.lower()
        row[DATA_COL] = doi
        row["Public Reshare?"] = reshare
        row["Derived License"] = (r.get("Derived License") or "").strip()
        row["Contributor"] = CONTRIBUTOR
        row["Date"] = date.today().strftime("%-m/%-d/%Y")
        out.append(row)
    return out, skipped


def main(argv):
    dry = "--dry-run" in argv
    verify = "--verify" in argv
    source = next((a for a in argv if not a.startswith("--")), None)

    dict_rows = load_rows(source)
    rows, skipped = backfill_rows(dict_rows)

    if verify:
        have = {r["table"]: r[DATA_COL] for r in csv.DictReader(
            open(STAGING_PATH, newline="", encoding="utf-8"))
            if r.get(DATA_COL)}
        want = {r["table"]: r[DATA_COL] for r in rows}
        missing = sorted(set(want) - set(have))
        extra = sorted(set(have) - set(want))
        differ = sorted(t for t in set(have) & set(want) if have[t] != want[t])
        for label, names in (("not staged", missing), ("staged but no longer a data DOI", extra),
                             ("value differs from the sheet", differ)):
            print(f"{len(names):>5}  {label}")
            for t in names[:10]:
                print(f"         {t}")
        return 1 if (missing or extra or differ) else 0

    print(f"{len(rows)} row(s) to stage under {DATA_COL}")
    if skipped:
        print(f"{len(skipped)} skipped:")
        for t, why in skipped:
            print(f"  {t}: {why}")
    if dry:
        for r in rows[:5]:
            print(f"  {r['table']:<40} {r[DATA_COL]}")
        return 0

    ##Rewritten, not appended: this is a one-off backfill of a known set, and
    ##appending it twice would name the same table twice, which read_dict_auto()
    ##refuses outright. So a previous run's rows are dropped and regenerated,
    ##while rows staged by stage_dict_row.py -- real dictionary rows for new
    ##tables -- are kept exactly as they are.
    existing = []
    if STAGING_PATH.exists():
        with open(STAGING_PATH, newline="", encoding="utf-8") as fh:
            existing = [r for r in csv.DictReader(fh) if not is_backfill_row(r)]
    staged = {r["table"] for r in existing}
    ##A table that already has a real staged row keeps it: that row carries a
    ##Description and a Reference, and adding a second is a duplicate, not a
    ##correction. Its DOI was routed by stage_dict_row.py on write anyway.
    rows = [r for r in rows if r["table"] not in staged]

    with open(STAGING_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(existing)
        w.writerows(rows)
    print(f"wrote {len(existing) + len(rows)} row(s) to {STAGING_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
