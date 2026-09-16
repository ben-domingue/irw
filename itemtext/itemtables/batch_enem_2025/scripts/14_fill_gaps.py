#!/usr/bin/env python3
"""Fill the items the accessibility booklet swaps away, from a standard booklet.

EXTRACTION_RULES.md R1.2 and R2. The accessibility booklet substitutes some
items for others, so a few published items have no text in it; they come from a
standard colour booklet instead.

The position of an item DIFFERS between colours -- 2019 CN item 54381 is at
position 120 in AZUL, 101 in AMARELA, 110 in CINZA, 96 in ROSA -- so the fill
must join at the CO_PROVA of the colour actually parsed, identified by TX_COR
among the year's standard_prova_codes. Joining at the wrong colour would attach
real text to the wrong item and every count would still look right.

Usage:
  python3 14_fill_gaps.py --year 2019 --colour AZUL \
      --parsed std_d1.csv std_d2.csv --items-dir <dir from 13_join.py>
"""
import argparse, csv, glob, json, os, re, sys

ENEM = os.path.expanduser("~/enem")
KEYS = set("ABCDE")
SCHEMA = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
          "item_text", "correct_response", "option_text", "resp", "item_text_translated",
          "option_text_translated", "instructions_translated", "section_prompt_translated",
          "language", "resp_raw"]


def itens(year):
    for pat in (f"{ENEM}/extracted_{year}/**/ITENS_PROVA_{year}.csv",
                f"{ENEM}/extracted_{year}/**/itens_prova_{year}.csv"):
        h = glob.glob(pat, recursive=True)
        if h:
            return list(csv.DictReader(open(h[0], encoding="latin-1"), delimiter=";"))
    sys.exit(f"no ITENS_PROVA for {year}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", required=True)
    ap.add_argument("--colour", required=True, help="TX_COR of the parsed standard booklet")
    ap.add_argument("--parsed", nargs="+", required=True)
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--manifest", default=f"{ENEM}/itemtext_run/allyears/manifest.json")
    a = ap.parse_args()
    year, colour = a.year, a.colour.upper()
    man = json.load(open(a.manifest))[str(year)]
    sc = set(man["standard_prova_codes"])
    rows_it = itens(year)
    has_aban = "IN_ITEM_ABAN" in rows_it[0]
    report = json.load(open(os.path.join(a.items_dir, "join_report.json")))

    parsed = []
    for p in a.parsed:
        parsed += list(csv.DictReader(open(p, encoding="utf-8")))
    # Key on (area, position, lang_block). An earlier version keyed on
    # (area, position) alone on the assumption that no filled item is ever in a
    # language block. 2018 falsifies that -- the 10 LC items needing a fill ARE
    # the language-block items -- and the result was both language versions
    # appended to each: ten option rows per item, letters A-E twice, two rows
    # with resp=1, and the gate passed anyway because it counts item codes.
    LANG_CODE = {"english": "0", "spanish": "1", "": ""}
    by_pos = {}
    for r in parsed:
        k = (r["area"], int(r["position"]), LANG_CODE.get(r["lang_block"], ""))
        by_pos.setdefault(k, []).append(r)

    filled_total = 0
    for area, missing in sorted(report["needs_standard"].items()):
        if not missing:
            continue
        prova = None
        for r in rows_it:
            if r["CO_PROVA"] in sc and r["SG_AREA"] == area and (r.get("TX_COR") or "").upper() == colour:
                prova = r["CO_PROVA"]; break
        if prova is None:
            print(f"    {area}: no standard CO_PROVA with TX_COR={colour} -- SKIPPED, escalate")
            continue
        sub = {r["CO_ITEM"]: r for r in rows_it if r["CO_PROVA"] == prova}
        table = f"enem_{year}_1mil_{area.lower()}"
        path = os.path.join(a.items_dir, f"{table}__items.csv")
        existing = list(csv.DictReader(open(path, encoding="utf-8")))
        have = {r["item"] for r in existing}
        # A filled item must carry the same `instructions` as the rest of its
        # table: one cover per table, not blank rows for the few items that came
        # from the other booklet. The two covers are near-identical anyway (2183
        # vs 2185 chars in 2019), and a table with two different values -- or
        # blanks on 5 of 225 rows -- would be a gratuitous inconsistency.
        tbl_instr = next((r["instructions"] for r in existing
                          if (r.get("instructions") or "").strip()), "")
        added = []
        for item in missing:
            rec = sub.get(item)
            if rec is None:
                print(f"    {area}: item {item} is not in the {colour} booklet either -- escalate")
                continue
            # The position convention is per-YEAR, and the filler must use the
            # same one the join used or it looks items up at the wrong printed
            # position. 2017 is per-area (CO_POSICAO 1-45 per area) while
            # 2018-2020 are continuous 1-180; joining CO_POSICAO straight to the
            # printed position filled 0 of 9 items in 2017. Read the convention
            # the joiner recorded rather than re-deriving it, so the two cannot
            # disagree.
            conv = (report.get("position_convention") or {}).get(area, "continuous")
            # Use the OFFSET the joiner measured, not a hardcoded day order.
            # {"LC":1,"CH":46,"CN":91,"MT":136} is the 2017+ order only; 2013-2016
            # print CH/CN on day 1 and LC/MT on day 2, and 2016 additionally
            # numbers CO_POSICAO in INEP's canonical LC/CH/CN/MT order, so its
            # offsets are CH -45, CN -45, LC +90, MT 0. derived_offset is 0 for a
            # plain continuous year, so this reproduces 2018-2020 unchanged.
            derived_off = (report.get("derived_offset") or {}).get(area, 0)
            cp = int(rec["CO_POSICAO"])
            ling = (rec.get("TP_LINGUA") or "").strip()
            if conv.startswith("continuous"):
                pos = cp + derived_off
            elif area == "LC":
                pos = cp if ling == "0" else cp - 5
            else:
                printed_lo = {"LC": 1, "CH": 46, "CN": 91, "MT": 136}[area]
                pos = cp + printed_lo - 1
            opts = by_pos.get((area, pos, ling))
            if opts is None and ling:
                print(f"    {area}: item {item} is a language-block item (TP_LINGUA={ling}) "
                      f"with no matching parsed block at printed position {pos} "
                      f"(CO_POSICAO {cp}, convention {conv}) -- escalate, not filled")
                continue
            if not opts:
                print(f"    {area}: item {item} at {colour} printed position {pos} "
                      f"(CO_POSICAO {cp}, convention {conv}) did not parse -- escalate")
                continue
            key = (rec["TX_GABARITO"] or "").strip()
            if key not in KEYS:
                print(f"    {area}: item {item} has no scorable key -- not shipped (R3)")
                continue
            if has_aban and (rec.get("IN_ITEM_ABAN") or "0").strip() not in ("0", ""):
                print(f"    {area}: item {item} IN_ITEM_ABAN with a valid key -- KEEP and disclose")
            stem = opts[0]["stem"]
            for o in sorted(opts, key=lambda x: x["option_letter"]):
                letter = o["option_letter"]
                existing.append({
                    "table": table, "section_id": f"{table}_1", "item": item,
                    "instrument": f"ENEM {year} - {area}", "instructions": tbl_instr,
                    "section_prompt": "", "item_text": stem, "correct_response": key,
                    "option_text": o["option_text"], "resp": 1 if letter == key else 0,
                    "item_text_translated": "", "option_text_translated": "",
                    "instructions_translated": "", "section_prompt_translated": "",
                    "language": "Portuguese", "resp_raw": letter})
            added.append(item)
        if added:
            existing.sort(key=lambda r: (r["item"], r["resp_raw"]))
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA); w.writeheader(); w.writerows(existing)
            filled_total += len(added)
            n_items = len({r["item"] for r in existing})
            print(f"  {table}: filled {len(added)} from {colour} ({added}) -> {n_items} items, {len(existing)} rows")
    print(f"\n  filled {filled_total} item(s) in total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
