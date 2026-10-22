#!/usr/bin/env python3
##Minneapolis ranked-choice tables: build with fairvote_cvr.py, check the source files, validate the tables.
##A thin wrapper. It does not convert anything itself: the tables and their design rows come from
##data/rankings/fairvote_cvr.py, the one script that builds every FairVote table.
##
##Usage (from the repository root):
##  python3 data/rankings/minneapolis/build_tables.py <raw dir> <out dir> --prefix rcv_mpls_20231107_
##  python3 data/rankings/minneapolis/build_tables.py <raw dir> <out dir> rcv_mpls_20231107_councilw6 [<table> ...]
##
##Steps:
##  1. Pick the tables: the names given, or every row of data/rankings/fairvote_manifest.csv whose table starts with --prefix.
##  2. Run `fairvote_cvr.py build <raw dir> <out dir> <tables>`. It downloads each raw file into <raw dir> if it is not
##     there yet, writes <out dir>/<table>.csv and refreshes the table's counts in design_tables.csv. Human fields
##     (seats, write_in_allowed, candidate_order, evidence) already recorded for a table are kept.
##  3. Source integrity: the size of each raw file must equal `filesize` in the manifest. The sha256 of each file is
##     printed, so a later run can show the file is the same. (The manifest md5 is not used: it does not match the files.)
##  4. Validate: `python3 -m irw_validate.rankings --design data/rankings/design_tables.csv <out dir>/*.csv`.
##Exit code: 0 all steps passed, 1 a step failed, 2 bad input.
##A build rewrites design_tables.csv beside fairvote_cvr.py. To try it without touching your checkout, run it in a
##scratch copy of the repository.
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

RANKINGS = Path(__file__).resolve().parent.parent
MANIFEST = RANKINGS / "fairvote_manifest.csv"
DESIGN = RANKINGS / "design_tables.csv"
BUILDER = RANKINGS / "fairvote_cvr.py"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Minneapolis ranked-choice tables with fairvote_cvr.py, check the source files, validate the tables.")
    ap.add_argument("raw_dir", type=Path, help="folder of FairVote raw files (downloaded into it if missing)")
    ap.add_argument("out_dir", type=Path, help="folder for the tables")
    ap.add_argument("tables", nargs="*", help="table names (default: every manifest row that starts with --prefix)")
    ap.add_argument("--prefix", default="", help="select the manifest rows whose table starts with this")
    args = ap.parse_args(argv)
    raw_dir, out_dir = args.raw_dir, args.out_dir
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        manifest = {r["table"]: r for r in csv.DictReader(f)}
    tables = args.tables or sorted(t for t in manifest if args.prefix and t.startswith(args.prefix))
    unknown = [t for t in tables if t not in manifest]
    if not tables or unknown:
        print(f"no such table in {MANIFEST.name}: {unknown or 'nothing selected'}", file=sys.stderr)
        return 2

    failed = 0
    if subprocess.run([sys.executable, str(BUILDER), "build", str(raw_dir), str(out_dir), *tables]).returncode:
        print("fairvote_cvr.py reported a warning or an error (see above)")
        failed += 1

    for t in tables:
        src = raw_dir / manifest[t]["filename"]
        size, want = src.stat().st_size, int(manifest[t]["filesize"])
        ok = size == want
        failed += not ok
        print(f"source {t}: size {size} {'equals' if ok else 'DIFFERS from'} the manifest ({want}), sha256 {sha256(src)}")

    check = [sys.executable, "-m", "irw_validate.rankings", "--design", str(DESIGN), *[str(out_dir / f"{t}.csv") for t in tables]]
    if subprocess.run(check).returncode:
        print("the validator reported a problem (see above)")
        failed += 1
    print("build: all steps passed" if not failed else f"build: {failed} step(s) failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
