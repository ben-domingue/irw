#!/usr/bin/env python3
"""Find option sets that are STACKED FRACTIONS split across lines.

Ben's point 4: two such items ship NA and eight ship the split text, which is
two treatments for one problem. Before any ruling can be applied consistently
we need the full list, not the ones that happened to be noticed.

Signature: the option is short, contains a newline, and the parts on either
side are numeric or near-numeric -- "17\\n70" is 17/70.
"""
import csv, collections, glob, os, re, sys

REPO = os.path.expanduser("~/irw/itemtext/itemtables")
YEARS = ["2013","2015","2016","2017","2018","2019","2020","2021","2022","2024","2025"]
NUMISH = re.compile(r"^[\d\s.,()−+\-×x*/^!πa-zA-Z]{1,24}$")

def looks_fraction(v):
    v = (v or "").strip()
    if "\n" not in v or len(v) > 40:
        return False
    parts = [p.strip() for p in v.split("\n") if p.strip()]
    if len(parts) < 2:
        return False
    return all(NUMISH.match(p) and any(c.isdigit() for c in p) for p in parts)

def main():
    found = []
    for y in YEARS:
        for p in sorted(glob.glob(f"{REPO}/batch_enem_{y}/*__items.csv")):
            a = re.search(r"_1mil_(\w\w)__", p).group(1)
            by = collections.defaultdict(list)
            for r in csv.DictReader(open(p, encoding="utf-8")):
                by[r["item"]].append(r)
            for it, rs in by.items():
                opts = [(r["resp_raw"], r["option_text"] or "") for r in rs]
                nf = sum(1 for _, v in opts if looks_fraction(v))
                if nf >= 2:
                    na = sum(1 for _, v in opts if v.strip() in ("", "NA"))
                    found.append((y, a.upper(), it, nf, na,
                                  "; ".join(f"{L}={v.strip()!r}" for L, v in opts)[:130]))
    print(f"  {len(found)} item(s) whose options are stacked fractions\n")
    per = collections.Counter(f[0] for f in found)
    print("  per year:", dict(sorted(per.items())))
    print()
    for y, a, it, nf, na, s in found:
        print(f"  {y} {a} {it}  ({nf} fraction-shaped, {na} NA)")
        print(f"      {s}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
