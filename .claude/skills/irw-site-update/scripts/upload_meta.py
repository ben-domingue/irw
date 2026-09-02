#!/usr/bin/env python3
"""Upload the regenerated metadata CSVs into datapages/irw_meta.

This is now a thin wrapper around `red_up`, which does the same work for every
IRW dataset -- see src/red_up/README.md. Everything this script used to do by
itself it still does, via red_up: the full-replace (delete the draft table and
recreate it, because Redivis uploads append), the preserved table description,
the stray-upload warning, and a post-upload row-count check. The check is now
an actual `select count(*)` rather than `numRows`, which the old comment here
already said could not be trusted.

Usage is unchanged:

    cd metadata
    python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py
    python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py biblio tags
    python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py --dry-run
    python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py --yes

Still never runs automatically: not from run_pipeline.sh, not from the weekly
cron. Still only ever writes the draft ("next") version -- review and publish
by hand on the Redivis site afterwards.
"""
import argparse
import sys
from pathlib import Path

# The fixed set of tables irw_meta holds. red_up also knows this list (as
# cli.META_TABLES) and excludes anything else, so this map's remaining job is
# to answer "which CSVs should I look for in --dir when no names are given".
# hero_stats.json is deliberately absent: it is not a Redivis table, it goes to
# the irw_site repo.
FILE_TABLE_MAP = {
    "metadata": "metadata",
    "biblio": "biblio",
    "tags": "tags",
    "nominal_tags": "nominal_tags",  # 03_tags.R nom branch, issue #1689; no comp/sim equivalent by design
    "comps_biblio": "comps_biblio",
    "nominal_biblio": "nominal_biblio",
    "simsyn_biblio": "simsyn_biblio",
    "simsyn_metadata": "simsyn_metadata",
    "comps_metadata": "comps_metadata",     # 05_comps.R fixed 2026-08-02
    "nominal_metadata": "nominal_metadata", # 06_nominal.R verified 2026-08-02
    "itemtext_metadata": "itemtext_metadata",  # 08_itemtext.R, 2026-08-02
    "collections": "collections",                # 10_collections.R, issue #1633
    "collection_members": "collection_members",  # 10_collections.R, issue #1633
}

SRC = next(p for p in Path(__file__).resolve().parents if (p / "red_up").is_dir())
sys.path.insert(0, str(SRC))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*",
                    help="file stems to upload (default: all known files present in --dir)")
    ap.add_argument("--dir", type=Path, default=Path("."),
                    help="directory to look for CSVs in (default: cwd)")
    ap.add_argument("--yes", "-y", action="store_true", help="skip the confirmation prompt")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, upload nothing")
    args = ap.parse_args()

    unknown = [n for n in args.names if n not in FILE_TABLE_MAP]
    if unknown:
        raise SystemExit(f"Unknown file(s) (not in FILE_TABLE_MAP): {unknown}")

    wanted = args.names or list(FILE_TABLE_MAP)
    files = [args.dir / f"{stem}.csv" for stem in wanted]
    files = [f for f in files if f.exists()]
    if not files:
        raise SystemExit(
            f"No known CSVs found in {args.dir.resolve()}. "
            f"Known names: {list(FILE_TABLE_MAP)}")

    argv = [str(f) for f in files] + ["--dataset", "irw_meta"]
    if args.yes:
        argv.append("--yes")
    if args.dry_run:
        argv.append("--dry-run")

    from red_up.cli import main as red_up_main

    return red_up_main(argv)


if __name__ == "__main__":
    sys.exit(main())
