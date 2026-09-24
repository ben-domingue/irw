#!/usr/bin/env python3
"""Trap 50's bugs + Ben's two greps, over item_text/option_text only."""
import csv, glob, re, sys, collections
sfx=sys.argv[1]
files=sorted(glob.glob(f"/scratch/users/mazzafe/itemtext_years/*/out{sfx}/*__items.csv"))
if not files: sys.exit(f"no files for out{sfx}")
CHECKS=[
 ("trap50 lowercase mid-word split (conf_orme)", re.compile(r"[a-zà-ÿ]{2,}_[a-zà-ÿ]{2,}"), 0),
 ("trap50 uppercase word split (T_ANTOS)",       re.compile(r"\b[A-Z]{2,}_[A-Z]{2,}\b"), 0),
 ("trap50 adjacent runs (10^-^4)",               re.compile(r"\^[^\s]{1,3}\^"), 0),
 ("Ben S1 spurious caret after subscript",       re.compile(r"[^\W\d_]+_\d+\^[^\W\d_]"), 0),
 ("Ben S2 unmarked trailing digits",             re.compile(r"\b[A-Z][a-z]?_\d+[A-Z][a-z]?\d+\b"), 0),
]
KEEP=[("H_3O^+ present", re.compile(r"H_3O\^\+")),
      ("total script markers", re.compile(r"[0-9A-Za-zà-ÿ][_^][0-9A-Za-zà-ÿ+\-−]"))]
cnt=collections.Counter(); ex=collections.defaultdict(list)
for f in files:
    for r in csv.DictReader(open(f)):
        for col in ("item_text","option_text"):
            v=r.get(col) or ""
            for name,rx,_ in CHECKS:
                for m in rx.finditer(v):
                    cnt[name]+=1
                    if len(ex[name])<6: ex[name].append((f.split('/')[-1],r["item"],m.group(0)))
            for name,rx in KEEP:
                cnt[name]+=len(rx.findall(v))
print(f"### out{sfx}  ({len(files)} files)")
bad=0
for name,_rx,want in CHECKS:
    ok = "ok " if cnt[name]==want else "FAIL"
    if cnt[name]!=want: bad+=1
    print(f"  [{ok}] {name:46} {cnt[name]}")
    for e in ex[name][:4]: print(f"            {e}")
for name,_rx in KEEP:
    print(f"  [    ] {name:46} {cnt[name]}")
sys.exit(0)
