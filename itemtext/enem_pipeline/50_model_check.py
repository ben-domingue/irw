#!/usr/bin/env python3
"""Ben's third check: can the EXTRACTED text be answered correctly?

Every other gate tests structure -- that the item set matches, that the keys
line up, that no glyph is out of range. None of them can tell you whether the
text still MEANS what the item meant. A stem missing its exponent, an option
whose denominator was lost, a passage that lost its final clause: all of those
leave item_set_match TRUE.

So: present the item exactly as a data user would receive it -- stem plus the
five option strings, nothing else, no PDF, no images -- and ask a model to
answer. Compare with TX_GABARITO.

HOW TO READ THE RESULT, because this is the part that is easy to get wrong:

  - This is NOT a score of the model, and NOT a pass/fail of the corpus. ENEM
    items are hard, many depend on a figure that no text can carry, and a
    model that answers 60% of figure-dependent items is doing well.
  - The signal is the COMPARISON BETWEEN STRATA, not the absolute number.
    Text-only items (LC prose, CH sources) should score far above chance. If
    they do not, the text is broken. Figure-dependent items will score lower
    for reasons that are not our fault, and that gap is expected.
  - A YEAR that scores markedly below its peers on text-only items is the
    alarm this is built to raise.
  - Every miss is a CANDIDATE for inspection, never a verdict.

Chance is 20%. Writes model_check.json with each answer so misses can be read.

Usage:
  python3 50_model_check.py --n 150 [--year 2013 ...] [--area lc] --out <json>
  python3 50_model_check.py --report <json>
"""
import argparse, collections, csv, glob, json, os, random, re, sys

REPO = os.path.expanduser("~/irw/itemtext/itemtables")
YEARS = ["2013","2015","2016","2017","2018","2019","2020","2021","2022","2024","2025"]

FIGURE_HINT = re.compile(
    r"gr[áa]fico|figura|esquema|imagem|tabela|mapa|diagrama|circuito|desenho|"
    r"quadro|ilustra|fotografia|charge|tirinha|cartum|obra|pintura", re.I)


def load_items(years, areas):
    out = []
    for y in years:
        for p in sorted(glob.glob(f"{REPO}/batch_enem_{y}/*__items.csv")):
            a = re.search(r"_1mil_(\w\w)__", p).group(1)
            if areas and a not in areas:
                continue
            by = collections.OrderedDict()
            for r in csv.DictReader(open(p, encoding="utf-8")):
                by.setdefault(r["item"], []).append(r)
            for it, rs in by.items():
                opts = {r["resp_raw"]: (r["option_text"] or "").strip() for r in rs}
                if any(v in ("", "NA") for v in opts.values()):
                    continue          # no text to answer from; not a fair test
                stem = rs[0]["item_text"]
                out.append({
                    "year": y, "area": a, "item": it,
                    "key": rs[0]["correct_response"],
                    "stem": stem, "options": opts,
                    "figure_dependent": bool(FIGURE_HINT.search(stem)),
                    "section_prompt": rs[0].get("section_prompt") or "",
                })
    return out


def prompt_for(d):
    p = []
    if d["section_prompt"] and d["section_prompt"] != "NA":
        p.append("TEXTO DE APOIO:\n" + d["section_prompt"])
    p.append("QUESTÃO:\n" + d["stem"])
    p.append("ALTERNATIVAS:")
    for L in "ABCDE":
        p.append(f"{L}) {d['options'].get(L,'')}")
    p.append("\nResponda apenas com a letra da alternativa correta (A, B, C, D ou E).")
    return "\n\n".join(p)


def report(path):
    d = json.load(open(path, encoding="utf-8"))
    rows = d["answers"]
    def acc(sel):
        s = [r for r in rows if sel(r)]
        if not s: return None, 0
        return sum(1 for r in s if r["correct"]) / len(s), len(s)
    print(f"  {len(rows)} item(s) answered from the extracted text alone. "
          f"Chance is 20%.\n")
    a, n = acc(lambda r: True)
    print(f"  overall                     {a:.0%}  (n={n})")
    for lbl, sel in (("text-only (no figure cue)", lambda r: not r["figure_dependent"]),
                     ("figure-dependent",          lambda r: r["figure_dependent"])):
        a, n = acc(sel)
        if a is not None: print(f"  {lbl:27s} {a:.0%}  (n={n})")
    print("\n  by year (text-only items, the diagnostic stratum):")
    for y in YEARS:
        a, n = acc(lambda r, y=y: r["year"] == y and not r["figure_dependent"])
        if a is not None:
            flag = "   <-- BELOW PEERS, inspect" if a < 0.45 and n >= 5 else ""
            print(f"     {y}  {a:.0%}  (n={n}){flag}")
    print("\n  by area:")
    for ar in ("ch", "cn", "lc", "mt"):
        a, n = acc(lambda r, ar=ar: r["area"] == ar)
        if a is not None: print(f"     {ar.upper()}  {a:.0%}  (n={n})")
    miss = [r for r in rows if not r["correct"]]
    print(f"\n  {len(miss)} miss(es) -- each is a CANDIDATE to inspect, not a verdict:")
    for r in miss[:25]:
        print(f"     {r['year']} {r['area'].upper()} {r['item']}  "
              f"key={r['key']} model={r['model']}  "
              f"{'figure' if r['figure_dependent'] else 'TEXT-ONLY'}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--year", action="append", default=[])
    ap.add_argument("--area", action="append", default=[])
    ap.add_argument("--out", default="model_check.json")
    ap.add_argument("--report")
    ap.add_argument("--seed", type=int, default=20260920)
    ap.add_argument("--dump-prompts", action="store_true")
    a = ap.parse_args()
    if a.report:
        return report(a.report)
    items = load_items(a.year or YEARS, set(a.area))
    random.Random(a.seed).shuffle(items)
    # stratify: proportional across year x area rather than a flat sample, so
    # one year cannot dominate and a per-year figure stays meaningful
    per = collections.defaultdict(list)
    for d in items:
        per[(d["year"], d["area"])].append(d)
    picked, i = [], 0
    while len(picked) < min(a.n, len(items)):
        keys = sorted(per)
        added = False
        for k in keys:
            if i < len(per[k]) and len(picked) < a.n:
                picked.append(per[k][i]); added = True
        if not added: break
        i += 1
    print(f"  {len(picked)} item(s) selected from {len(items)} answerable "
          f"(items with any NA option are excluded as unanswerable)")
    out = {"n": len(picked), "seed": a.seed, "answers": [], "prompts": []}
    for d in picked:
        rec = {k: d[k] for k in ("year","area","item","key","figure_dependent")}
        rec["prompt"] = prompt_for(d)
        out["prompts"].append(rec)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  prompts -> {a.out}  (answer them, then fill answers[] and --report)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
