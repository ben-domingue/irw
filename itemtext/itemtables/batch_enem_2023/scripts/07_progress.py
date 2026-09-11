#!/usr/bin/env python3
"""Translation progress for the ENEM 2023 item text build."""
import csv, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
tr = json.load(open(os.path.join(HERE, "translations_2023.json"), encoding="utf-8"))
items, instr = tr.get("items", {}), tr.get("instructions", {})

print(f"instructions: {len(instr)}/4 areas")
tot_i = tot_d = tot_r = tot_rd = 0
for p in sorted(glob.glob(os.path.join(HERE, "enem_2023_1mil_*__items.csv"))):
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    by = {}
    for r in rows: by.setdefault(r["item"], []).append(r)
    done = [i for i in by if items.get(i, {}).get("stem", "").strip()
            and len(items[i].get("options", {})) == 5]
    rdone = sum(len(by[i]) for i in done)
    a = os.path.basename(p).split("__")[0]
    bar = "#" * round(20 * len(done) / len(by)) + "." * (20 - round(20 * len(done) / len(by)))
    print(f"  {a:22} [{bar}] {len(done):>3}/{len(by):<3} items  {rdone:>3}/{len(by and rows):<3} rows")
    tot_i += len(by); tot_d += len(done); tot_r += len(rows); tot_rd += rdone
pct = 100 * tot_d / tot_i if tot_i else 0
print(f"  {'TOTAL':22} {tot_d}/{tot_i} items ({pct:.1f}%)   {tot_rd}/{tot_r} rows")
print("STATUS:", "COMPLETE" if tot_d == tot_i else f"{tot_i - tot_d} items remaining")
