#!/usr/bin/env python3
"""Per-year source manifest for ENEM item-text extraction.

Implements EXTRACTION_RULES.md R0, R2 and R3 once, centrally, so no per-year
worker re-derives them and none can diverge. Output is a JSON manifest plus a
readable table.

For each year and area it records:
  - standard_prova_codes, read out of data/enem_<YYYY>.R (never assumed)
  - the published item set (ITENS_PROVA at those codes)
  - the accessibility CO_PROVA, chosen as the LARANJA/LEDOR booklet with the
    largest overlap with the published set -- the first application, not a
    reapplication booklet that happens to share the colour
  - std-minus-acc: items the accessibility booklet swaps away, which must come
    from the standard booklet PDF
  - acc-minus-std: items only in the accessibility booklet, which are NOT in
    the response tables and must not ship
  - items INEP flags IN_ITEM_ABAN with a valid key (kept, must be disclosed)
  - items with no scorable key (dropped by #1942, no text ships)
  - the booklet files actually on disk, per day

It asserts nothing and fixes nothing: a year that looks wrong is reported so a
human decides. Usage: python3 10_year_manifest.py [--json out.json]
"""
import csv, glob, json, os, re, sys

ENEM = os.path.expanduser("~/enem")
REPO = os.path.expanduser("~/irw")
AREAS = ("CH", "LC", "CN", "MT")
KEYS = set("ABCDE")


def std_codes(year):
    p = f"{REPO}/data/enem_{year}.R"
    if not os.path.exists(p):
        return None
    m = re.search(r"standard_prova_codes\s*<-\s*c\(([^)]*)\)", open(p, encoding="utf-8").read())
    return {c.strip() for c in m.group(1).split(",")} if m else None


def itens_file(year):
    for pat in (f"{ENEM}/extracted_{year}/**/ITENS_PROVA_{year}.csv",
                f"{ENEM}/extracted_{year}/**/itens_prova_{year}.csv"):
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    return None


def booklets(year):
    """Every prova/gabarito file on disk, bucketed. Naming differs every year,
    so this reports what is there rather than asserting a pattern."""
    out = {"accessibility": [], "standard": [], "dosvox": [], "other": []}
    for f in glob.glob(f"{ENEM}/extracted_{year}/**/*", recursive=True):
        if not os.path.isfile(f):
            continue
        base = os.path.basename(f)
        if not re.search(r"PROVAS", f, re.I):
            continue
        if re.search(r"GAB", base, re.I):
            continue
        if re.search(r"DOSVOX", base, re.I):
            out["dosvox"].append(base)
        elif re.search(r"(LEDOR|LARANJA|BRAIL)", base, re.I):
            out["accessibility"].append(base)
        elif re.search(r"(AMPLIAD|LIBRAS|NVDA|DIGITAL)", base, re.I):
            out["other"].append(base)
        elif re.search(r"\.pdf$", base, re.I):
            out["standard"].append(base)
    return {k: sorted(v) for k, v in out.items()}


def main():
    manifest = {}
    print(f"  {'year':<5} {'area':<4} {'pub':>4} {'acc_prova':>9} {'needs_std':>9} "
          f"{'acc_only':>8} {'aban_kept':>9} {'nokey':>5}")
    for year in range(2013, 2026):
        sc, itf = std_codes(year), itens_file(year)
        entry = {"standard_prova_codes": sorted(sc) if sc else None,
                 "itens_file": os.path.basename(itf) if itf else None,
                 "booklets": booklets(year), "areas": {}, "problems": []}
        if not sc or not itf:
            entry["problems"].append("missing year script codes or ITENS_PROVA file")
            manifest[year] = entry
            print(f"  {year:<5} -- {entry['problems'][-1]}")
            continue
        rows = list(csv.DictReader(open(itf, encoding="latin-1"), delimiter=";"))
        has_aban = "IN_ITEM_ABAN" in rows[0]
        has_cor = "TX_COR" in rows[0]
        for area in AREAS:
            pub = {r["CO_ITEM"] for r in rows if r["CO_PROVA"] in sc and r["SG_AREA"] == area}
            if not pub:
                entry["areas"][area] = {"problem": "no published items at the standard codes"}
                continue
            acc_prova, acc_items = None, set()
            if has_cor:
                best = None
                for p in {r["CO_PROVA"] for r in rows
                          if r["SG_AREA"] == area and re.search(r"(LARANJA|LEDOR)", r.get("TX_COR") or "", re.I)}:
                    li = {r["CO_ITEM"] for r in rows if r["CO_PROVA"] == p}
                    ov = len(pub & li)
                    if best is None or ov > best[1]:
                        best = (p, ov, li)
                if best and best[1]:
                    acc_prova, acc_items = best[0], best[2]
            keyof = {r["CO_ITEM"]: r["TX_GABARITO"] for r in rows if r["SG_AREA"] == area}
            aban = set()
            if has_aban:
                aban = {r["CO_ITEM"] for r in rows if r["SG_AREA"] == area
                        and (r.get("IN_ITEM_ABAN") or "0").strip() not in ("0", "")}
            a = {
                "published_items": sorted(pub),
                "accessibility_co_prova": acc_prova,
                "needs_standard_booklet": sorted(pub - acc_items) if acc_prova else sorted(pub),
                "accessibility_only_do_not_ship": sorted(acc_items - pub) if acc_prova else [],
                "aban_kept_valid_key": sorted(i for i in (aban & pub) if keyof.get(i) in KEYS),
                "no_scorable_key_not_shipped": sorted(i for i in pub if keyof.get(i) not in KEYS),
            }
            entry["areas"][area] = a
            print(f"  {year:<5} {area:<4} {len(pub):>4} {str(acc_prova or '-'):>9} "
                  f"{len(a['needs_standard_booklet']):>9} {len(a['accessibility_only_do_not_ship']):>8} "
                  f"{len(a['aban_kept_valid_key']):>9} {len(a['no_scorable_key_not_shipped']):>5}")
        if not entry["booklets"]["accessibility"] and not entry["booklets"]["dosvox"]:
            entry["problems"].append("no accessibility booklet or DOSVOX file on disk")
        if not entry["booklets"]["standard"]:
            entry["problems"].append("no standard booklet PDF on disk")
        manifest[year] = entry
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(manifest, open(out, "w"), indent=1, sort_keys=True)
        print(f"\n  written: {out}")
    print("\n  years with problems:")
    for y, e in manifest.items():
        if e["problems"]:
            print(f"    {y}: {'; '.join(e['problems'])}")


if __name__ == "__main__":
    main()
