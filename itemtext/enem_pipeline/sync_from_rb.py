#!/usr/bin/env python3
"""Sync the committed tables from the canonical build, content-only.

committed == out_rb with empty fields written as literal NA (what
normalize_nulls.R does). Only item_text and option_text are synced; if any
OTHER column differs, that is reported and nothing is written, because it
would mean the build changed something this sync was not asked to carry.
"""
import csv, glob, os, sys
sys.path.insert(0, "/home/users/mazzafe/enem/itemtext_run/allyears")
from _rcsv import write_r_csv, quoted_columns

T = "/scratch/users/mazzafe/itemtext_years"
REPO = "/home/users/mazzafe/irw/itemtext/itemtables"
SYNC = ("item_text", "option_text")
apply_ = "--apply" in sys.argv
tot_cells = tot_files = 0
problems = []
for src in sorted(glob.glob(f"{T}/*/out_rb/*__items.csv")):
    y = src.replace(T + "/", "").split("/")[0]
    name = os.path.basename(src)
    dst = os.path.join(REPO, f"batch_enem_{y}", name)
    if not os.path.exists(dst):
        problems.append((y, name, "not committed")); continue
    a = list(csv.DictReader(open(src, encoding="utf-8")))
    b = list(csv.DictReader(open(dst, encoding="utf-8")))
    if len(a) != len(b):
        problems.append((y, name, f"row count {len(a)} vs {len(b)}")); continue
    if [(r["item"], r["resp_raw"]) for r in a] != [(r["item"], r["resp_raw"]) for r in b]:
        problems.append((y, name, "row keys differ")); continue
    other = 0
    for x, z in zip(a, b):
        for col in z:
            if col in SYNC:
                continue
            if x.get(col, "") != z.get(col, "") and not (x.get(col, "") == "" and z.get(col) == "NA"):
                other += 1
    if other:
        problems.append((y, name, f"{other} non-text field(s) differ -- not synced")); continue
    n = 0
    for x, z in zip(a, b):
        for col in SYNC:
            new = x.get(col, "")
            if new == "" and z.get(col) == "NA":
                new = "NA"                      # normalize_nulls.R's convention
            if z.get(col, "") != new:
                z[col] = new; n += 1
    if n:
        tot_cells += n; tot_files += 1
        print(f"  {y} {name:32} {n} cell(s)")
        if apply_:
            write_r_csv(dst, list(b[0].keys()), b, quoted_columns(dst))
print(f"\n{tot_cells} cells across {tot_files} files {'SYNCED' if apply_ else 'would sync'}")
if problems:
    print("\nPROBLEMS -- these files were NOT synced:")
    for p in problems:
        print("   ", p)
    sys.exit(1)
