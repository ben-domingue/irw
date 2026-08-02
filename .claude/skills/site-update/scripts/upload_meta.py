#!/usr/bin/env python3
"""Replace the metadata/biblio/tags Redivis tables with the local CSVs this
skill regenerates (workflow 1: run_pipeline.sh).

This is the manual-merge step workflow 1's own docs describe as "outside
this skill's scope" -- it now IS in scope, as an explicit, confirmed action
distinct from the read-only generate/diff/audit steps. It still never runs
automatically as part of run_pipeline.sh or audit_tables.R.

Only ever touches redivis.user("bdomingu").dataset("irw_meta", version="next")
-- a draft version. After running this, review the draft on the Redivis site
and publish it by hand; nothing here publishes automatically.

Fixed file -> table mapping (confirmed against the live dataset 2026-08-02;
each table's qualified reference -- e.g. "metadata:h5gs" -- was resolved via
a read-only token, see FILE_TABLE_MAP below). hero_stats.json is NOT in this
list -- it's not a Redivis table, it goes to the separate irw_site repo.

Usage (run from metadata/, same convention as the other pipeline scripts):
    cd metadata
    python3 ../.claude/skills/site-update/scripts/upload_meta.py            # all known files present in cwd
    python3 ../.claude/skills/site-update/scripts/upload_meta.py biblio tags # only these
    python3 ../.claude/skills/site-update/scripts/upload_meta.py --dry-run  # show plan, upload nothing
    python3 ../.claude/skills/site-update/scripts/upload_meta.py --yes      # skip the confirmation prompt

Credentials: reuses the same write-scoped (data.edit) REDIVIS_API_TOKEN
already used by data/add2redivis/upload.py, loaded from that script's own
.env file. This is deliberately a *different* token from ~/.redivis_api_token
(the read-only one run_pipeline.sh/audit_tables.R use) -- that one lacks
data.edit scope, confirmed 2026-08-02 (403 insufficient_scope on every table
in this dataset). An already-exported REDIVIS_API_TOKEN env var wins over
the .env file, same precedence as add2redivis/upload.py.
"""
import argparse
import os
import sys
from pathlib import Path

# file stem (no .csv) -> Redivis table name within bdomingu/irw_meta
FILE_TABLE_MAP = {
    "metadata": "metadata",
    "biblio": "biblio",
    "tags": "tags",
    "comps_biblio": "comps_biblio",
    "nominal_biblio": "nominal_biblio",
    "simsyn_biblio": "simsyn_biblio",
    "simsyn_metadata": "simsyn_metadata",
    "comps_metadata": "comps_metadata",   # 05_comps.R is broken as of 2026-07-28 (see TODO.md) -- rarely present
    "nominal_metadata": "nominal_metadata",  # 06_nominal.R excluded from run_pipeline.sh's default order
}

ADD2REDIVIS_ENV = Path(__file__).resolve().parents[5] / "data" / "add2redivis" / ".env"


def load_token() -> str:
    token = os.getenv("REDIVIS_API_TOKEN")
    if token:
        return token
    try:
        from dotenv import load_dotenv
    except ImportError:
        raise SystemExit("Missing dependency: pip install python-dotenv")
    if not ADD2REDIVIS_ENV.exists():
        raise SystemExit(
            f"No REDIVIS_API_TOKEN in env, and {ADD2REDIVIS_ENV} not found.\n"
            "Either export REDIVIS_API_TOKEN yourself (must have data.edit scope "
            "for bdomingu/irw_meta), or point ADD2REDIVIS_ENV at the right .env file."
        )
    load_dotenv(dotenv_path=ADD2REDIVIS_ENV)
    token = os.getenv("REDIVIS_API_TOKEN")
    if not token:
        raise SystemExit(f"{ADD2REDIVIS_ENV} exists but has no REDIVIS_API_TOKEN in it.")
    return token


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

    print("Plan -- local file -> bdomingu/irw_meta (version=next) table, full replace:")
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
    dataset = redivis.user("bdomingu").dataset("irw_meta", version="next")

    for stem, path in files.items():
        table_name = FILE_TABLE_MAP[stem]
        table = dataset.table(table_name)

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
        print(f"  done: {table_name}")

    print("\nAll uploads complete on the 'next' (draft) version of bdomingu/irw_meta.")
    print("Nothing is live yet -- review and publish the new version on the Redivis site.")


if __name__ == "__main__":
    main()
