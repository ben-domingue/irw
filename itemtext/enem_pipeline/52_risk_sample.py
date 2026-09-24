#!/usr/bin/env python3
"""Select the items most LIKELY to be damaged, for the model-understanding check.

A random sample measures the average item. What we want to know is whether the
items we TOUCHED, or that came through the riskiest paths, still read
correctly. So score each item by how much intervention it received and how
exotic its source was, and take the top N.

Risk factors, each one a thing that could have broken the text:
  +3  carries a ^ or _ marker            (5 bugs shipped before this settled)
  +3  option text was rewritten as a/b   (stacked-fraction inlining)
  +4  transcribed or patched by hand
  +3  carries an AI-generated notation note
  +2  from a font-repaired year          (2015/2016/2018 CFF, 2021, 2022 Symbol)
  +2  option letters were stripped       (2022, 880 rows)
  +2  gap-filled from a standard booklet
  +1  contains an unusual character
  +1  stem under 400 chars               (little context to self-correct)
  +1  option text under 3 chars
"""
import argparse, collections, csv, glob, json, os, re, sys

REPO = os.path.expanduser("~/irw/itemtext/itemtables")
YEARS = ["2013","2015","2016","2017","2018","2019","2020","2021","2022","2024","2025"]
REPAIRED = {"2015","2016","2018","2021","2022"}
STRIPPED = {"2022"}
HAND = {"14712","60291","86572","51219","43849","86840"}
ODD = re.compile(r"[^\x00-\x7fÀ-ÿ‘’“”–—…"
                 r"ºª°•·§]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--out", default="risk_sample.json")
    a = ap.parse_args()
    scored = []
    for y in YEARS:
        for p in sorted(glob.glob(f"{REPO}/batch_enem_{y}/*__items.csv")):
            ar = re.search(r"_1mil_(\w\w)__", p).group(1)
            by = collections.OrderedDict()
            for r in csv.DictReader(open(p, encoding="utf-8")):
                by.setdefault(r["item"], []).append(r)
            for it, rs in by.items():
                opts = {r["resp_raw"]: (r["option_text"] or "").strip() for r in rs}
                if any(v in ("", "NA") for v in opts.values()):
                    continue                       # unanswerable, not a fair test
                stem = rs[0]["item_text"] or ""
                blob = stem + " ".join(opts.values())
                s, why = 0, []
                if "^" in blob or "_" in blob: s += 3; why.append("script-marker")
                if any(re.fullmatch(r"[\d\s./^!×x,+\-−()]+", v) and "/" in v
                       for v in opts.values()): s += 3; why.append("fraction")
                if it in HAND: s += 4; why.append("hand-transcribed")
                if "gerada por IA" in stem: s += 3; why.append("AI-note")
                if y in REPAIRED: s += 2; why.append("font-repaired")
                if y in STRIPPED: s += 2; why.append("letter-stripped")
                if ODD.search(blob): s += 1; why.append("odd-char")
                if len(stem) < 400: s += 1; why.append("short-stem")
                if any(len(v) < 3 for v in opts.values()): s += 1; why.append("tiny-option")
                if s == 0:
                    continue
                scored.append({"year": y, "area": ar, "item": it,
                               "key": rs[0]["correct_response"], "risk": s,
                               "why": why, "stem": stem, "options": opts,
                               "section_prompt": rs[0].get("section_prompt") or ""})
    scored.sort(key=lambda d: -d["risk"])
    # spread across years so one year cannot dominate the top of the list
    per = collections.defaultdict(list)
    for d in scored:
        per[d["year"]].append(d)
    out, i = [], 0
    while len(out) < min(a.n, len(scored)):
        added = False
        for y in YEARS:
            if i < len(per[y]) and len(out) < a.n:
                out.append(per[y][i]); added = True
        if not added:
            break
        i += 1
    print(f"  {len(scored)} items carry at least one risk factor; taking {len(out)}")
    print("  risk score distribution in the sample:",
          dict(sorted(collections.Counter(d["risk"] for d in out).items(), reverse=True)))
    print("  factors:", dict(collections.Counter(
        w for d in out for w in d["why"]).most_common()))
    json.dump({"n": len(out), "items": out}, open(a.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"  -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
