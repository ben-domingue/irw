#!/usr/bin/env python3
"""Replace the metadata/biblio/tags Redivis tables with the local CSVs this
skill regenerates (workflow 1: run_pipeline.sh).

This is the manual-merge step workflow 1's own docs describe as "outside
this skill's scope" -- it now IS in scope, as an explicit, confirmed action
distinct from the read-only generate/diff/audit steps. It still never runs
automatically as part of run_pipeline.sh or audit_tables.R.

Only ever touches redivis.user("datapages").dataset("irw_meta", version="next")
-- a draft version. After running this, review the draft on the Redivis site
and publish it by hand; nothing here publishes automatically.

Fixed file -> table mapping (confirmed against the live dataset 2026-08-02;
each table's qualified reference -- e.g. "metadata:h5gs" -- was resolved via
a read-only token, see FILE_TABLE_MAP below). hero_stats.json is NOT in this
list -- it's not a Redivis table, it goes to the separate irw_site repo.

Usage (run from metadata/, same convention as the other pipeline scripts):
    cd metadata
    python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py            # all known files present in cwd
    python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py biblio tags # only these
    python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py --dry-run  # show plan, upload nothing
    python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py --yes      # skip the confirmation prompt

Credentials: the write-scoped (data.edit) REDIVIS_API_TOKEN, resolved by the
shared helper in src/irw_secrets.py -- normally ~/.config/irw/redivis-write.env,
with an already-exported env var winning. This is deliberately a *different*
token from ~/.redivis_api_token (the read-only one run_pipeline.sh/audit_tables.R
use) -- that one lacks data.edit scope, confirmed 2026-08-02 (403
insufficient_scope on every table in this dataset).
"""
import argparse
import os
import sys
from pathlib import Path

# file stem (no .csv) -> Redivis table name within datapages/irw_meta
FILE_TABLE_MAP = {
    "metadata": "metadata",
    "biblio": "biblio",
    "tags": "tags",
    "construct_descriptions": "construct_descriptions",  # 03b_describe.R, issue #1406; paraphrased only -- never the sheet's raw Context Text
    "nominal_tags": "nominal_tags",  # 03_tags.R nom branch, issue #1689; no comp/sim equivalent by design
    "comps_biblio": "comps_biblio",
    "nominal_biblio": "nominal_biblio",
    "simsyn_biblio": "simsyn_biblio",
    "simsyn_metadata": "simsyn_metadata",
    "comps_metadata": "comps_metadata",     # 05_comps.R fixed 2026-08-02, back in run_pipeline.sh's default order
    "nominal_metadata": "nominal_metadata", # 06_nominal.R verified working 2026-08-02, likewise
    "itemtext_metadata": "itemtext_metadata",  # 08_itemtext.R joined the default order 2026-08-02
}

sys.path.insert(0, str(next(
    p for p in Path(__file__).resolve().parents
    if (p / "src" / "irw_secrets.py").is_file()) / "src"))
from irw_secrets import load_write_token


def load_token() -> str:
    return load_write_token(__file__)


def discover_files(dir_path: Path, names: list[str]) -> dict[str, Path]:
    wanted = names or list(FILE_TABLE_MAP)
    unknown = [n for n in wanted if n not in FILE_TABLE_MAP]
    if unknown:
        raise SystemExit(f"Unknown file(s) (not in FILE_TABLE_MAP): {unknown}")
    found = {}
    for stem in wanted:
        p = dir_path / f"{stem}.csv"
        if p.exists():
            found[stem] = p
    return found


def count_rows(path: Path) -> int:
    import csv
    with open(path, "r", encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1  # minus header


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="file stems to upload (default: all known files present in --dir)")
    ap.add_argument("--dir", type=Path, default=Path("."), help="directory to look for CSVs in (default: cwd)")
    ap.add_argument("--yes", "-y", action="store_true", help="skip the confirmation prompt")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, upload nothing")
    args = ap.parse_args()

    files = discover_files(args.dir, args.names)
    if not files:
        print(f"No known CSVs found in {args.dir.resolve()}. Known names: {list(FILE_TABLE_MAP)}")
        sys.exit(1)

    print("Plan -- local file -> datapages/irw_meta (version=next) table, full replace:")
    for stem, path in files.items():
        print(f"  {path}  ({count_rows(path)} data rows)  ->  {FILE_TABLE_MAP[stem]}")

    if args.dry_run:
        print("\n--dry-run: nothing uploaded.")
        return

    if not args.yes:
        resp = input("\nProceed with upload? This replaces each table's data on the 'next' (draft) "
                      "version -- you'll still need to review and publish on the Redivis site "
                      "afterward. (y/n) ").strip().lower()
        if resp != "y":
            print("Aborted.")
            return

    token = load_token()
    os.environ["REDIVIS_API_TOKEN"] = token
    import redivis
    redivis.authenticate()
    dataset = redivis.user("datapages").dataset("irw_meta", version="next")

    mismatches = []
    for stem, path in files.items():
        table_name = FILE_TABLE_MAP[stem]
        table = dataset.table(table_name)
        expected = count_rows(path)

        try:
            existing_uploads = [u.name for u in table.list_uploads()]
        except Exception as e:
            print(f"  ! {table_name}: could not list existing uploads ({e}) -- proceeding anyway")
            existing_uploads = []
        stray = [u for u in existing_uploads if u != table_name]
        if stray:
            print(f"  ! {table_name}: found other upload(s) besides '{table_name}' already on this table: "
                  f"{stray} -- replace_on_conflict only replaces the upload named '{table_name}'; "
                  "these will NOT be removed and may leave stale rows. Check on the Redivis site.")

        print(f"Uploading {path} -> {table_name} ...")
        upload = table.upload(table_name)
        with open(path, "rb") as f:
            upload.create(
                f,
                type="delimited",
                remove_on_fail=True,
                wait_for_finish=True,
                raise_on_fail=True,
                replace_on_conflict=True,
            )
        # Verify the table really ends up holding the rows we just uploaded. A
        # successful upload call does NOT imply a successful *replace*:
        # replace_on_conflict only replaces an upload whose name matches, and a
        # draft table can carry rows inherited from the released version that
        # list_uploads() does not expose. When that happens the new rows land
        # BESIDE the old ones and the table silently doubles -- exactly what
        # happened to comps_metadata (23 unique rows -> 90 -> 180 across
        # successive weekly runs, found 2026-08-24, with the stray-upload check
        # above seeing nothing because there was no listable stray upload).
        # Comparing numRows here turns that silent corruption into a loud
        # failure on the first run it happens.
        try:
            actual = table.get().properties.get("numRows")
            actual = int(actual) if actual is not None else None
        except Exception as e:
            print(f"  ! {table_name}: uploaded, but could not read back numRows ({e}) -- VERIFY BY HAND")
            mismatches.append((table_name, expected, "unknown"))
            continue

        if actual == expected:
            print(f"  done: {table_name}  ({actual} rows, matches local)")
        else:
            print(f"  !! {table_name}: expected {expected} rows, table now has {actual}")
            if actual is not None and actual > expected:
                print("     Rows were APPENDED, not replaced -- this table is holding data the "
                      "upload did not replace (typically inherited from the released version and "
                      "not listed as an upload). Fix on the Redivis site: delete the table's "
                      "existing data (or the table itself) on the 'next' draft, then re-run this "
                      "script for just this file.")
            mismatches.append((table_name, expected, actual))

    if mismatches:
        print(f"\n*** UPLOAD VERIFICATION FAILED for {len(mismatches)} of {len(files)} table(s):")
        for name, exp, act in mismatches:
            print(f"      {name}: expected {exp}, got {act}")
        print("    Do NOT publish the draft version until these are resolved.")
        sys.exit(1)

    print("\nAll uploads complete and row-count verified on the 'next' (draft) version "
          "of datapages/irw_meta.")
    print("Nothing is live yet -- review and publish the new version on the Redivis site.")


if __name__ == "__main__":
    main()
