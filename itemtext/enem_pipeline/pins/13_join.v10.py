#!/usr/bin/env python3
"""Join parsed booklet text to INEP's item codes and emit the four __items.csv.

EXTRACTION_RULES.md R0: `item` is CO_ITEM from ITENS_PROVA_<YYYY>.csv, reached
by joining the booklet's printed position (and TP_LINGUA for the LC language
block) at the accessibility CO_PROVA. Nothing here invents a code.

TP_LINGUA is 0=Inglês, 1=Espanhol, per INEP's own data dictionary
(Dicionário_Microdados_Enem_<YYYY>.xlsx, sheet ITENS_PROVA_<YYYY>) -- read
rather than assumed, because getting it backwards would silently swap the
English and Spanish items, and both have 5 items so no count would reveal it.

Applies R3 (no scorable key -> not shipped; IN_ITEM_ABAN with a valid key ->
kept and reported for disclosure), R6 (no translations) and R7 (schema).
Reports, and does not resolve: positions with no match, items in the published
set that this booklet does not carry (R2 -- they need the standard booklet),
and items whose options came out empty (R5 candidates).

Usage:
  python3 13_join.py --year 2019 --parsed p_d1.csv p_d2.csv --out-dir <dir>
"""
import argparse, csv, glob, json, os, re, sys

ENEM = os.path.expanduser("~/enem")
REPO = os.path.expanduser("~/irw")
AREAS = ("CH", "LC", "CN", "MT")
KEYS = set("ABCDE")
SCHEMA = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
          "item_text", "correct_response", "option_text", "resp", "item_text_translated",
          "option_text_translated", "instructions_translated", "section_prompt_translated",
          "language", "resp_raw"]
LANG_CODE = {"english": "0", "spanish": "1", "": ""}
# screen-reader-only instruction lines: candidates in the response tables sat the
# standard booklets and never read these (R7, ruled 2026-09-11 for 2023)
SCREEN_READER = re.compile(r"(soletrar|leitor de tela|sintetizador|dosvox|nvda)", re.I)


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
    ap.add_argument("--parsed", nargs="+", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--manifest", default=os.path.expanduser(
        "~/enem/itemtext_run/allyears/manifest.json"))
    ap.add_argument("--colour", default=None,
                    help="TX_COR of a STANDARD booklet, for years with no "
                         "accessibility edition (2013, 2015, 2016)")
    a = ap.parse_args()
    year = a.year
    man = json.load(open(a.manifest))[str(year)]
    rows_it = itens(year)
    has_aban = "IN_ITEM_ABAN" in rows_it[0]

    parsed = []
    for p in a.parsed:
        parsed += list(csv.DictReader(open(p, encoding="utf-8")))
    # R7: instructions is the booklet cover, screen-reader lines already
    # stripped by the parser. One cover per booklet, so map it onto the areas
    # that booklet carries. Previously this dict was never populated and every
    # row of every year shipped a blank `instructions`.
    cover = {}
    for pth in a.parsed:
        cov = pth + ".cover.txt"
        if not os.path.exists(cov):
            continue
        txt = open(cov, encoding="utf-8").read().strip()
        areas_here = {r["area"] for r in csv.DictReader(open(pth, encoding="utf-8"))}
        for ar in areas_here:
            if txt and not cover.get(ar):
                cover[ar] = txt
    # Shared passages (R7, ruled 2026-09-15): a passage serving several items is
    # carried ONCE in section_prompt on its own section_id, not repeated into
    # each item_text. The parser records them alongside its output.
    shared = {}         # (area, position) -> (section_suffix, passage text)
    for pth in a.parsed:
        sp = pth + ".shared_passages.csv"
        if not os.path.exists(sp):
            continue
        for k, row in enumerate(csv.DictReader(open(sp, encoding="utf-8")), start=2):
            for pos in str(row.get("attached") or "").split():
                shared[(row["area"], int(pos))] = (k, row["text"])
    if shared:
        print(f"  shared passages: {len({v[0] for v in shared.values()})} passage(s) "
              f"over {len(shared)} item position(s) -> section_prompt")

    by_item = {}        # (area, pos, lingua) -> list of option rows
    for r in parsed:
        by_item.setdefault((r["area"], int(r["position"]), LANG_CODE[r["lang_block"]]), []).append(r)

    os.makedirs(a.out_dir, exist_ok=True)
    report = {"unmatched": [], "needs_standard": {}, "aban_kept": {},
              "no_key_skipped": {}, "empty_options": []}

    for area in AREAS:
        info = man["areas"].get(area) or {}
        prova = info.get("accessibility_co_prova")
        if not prova and a.colour:
            # 2013, 2015 and 2016 have no accessibility edition at all, so the
            # text comes from a standard colour booklet. Require exactly ONE
            # candidate at that colour: more than one means the colour is
            # ambiguous for this area and that is a reportable problem, not
            # something to pick from.
            sc = set(man["standard_prova_codes"])
            cands = sorted({r["CO_PROVA"] for r in rows_it
                            if r["CO_PROVA"] in sc and r["SG_AREA"] == area
                            and (r.get("TX_COR") or "").upper() == a.colour.upper()})
            if len(cands) == 1:
                prova = cands[0]
                report.setdefault("standard_booklet_co_prova", {})[area] = prova
            else:
                report.setdefault("ambiguous_colour", {})[area] = cands
        if not prova:
            report.setdefault("no_accessibility_booklet", []).append(area)
            continue
        sub = [r for r in rows_it if r["CO_PROVA"] == prova]
        # printed positions this booklet actually used for this area, from the
        # parse -- NOT a hardcoded day order, which differs before 2017.
        seen_pos = sorted({p for (ar, p, lg) in by_item if ar == area and not lg})
        cps_shared = sorted(int(r["CO_POSICAO"]) for r in sub
                            if not (r.get("TP_LINGUA") or "").strip())
        printed_lo = seen_pos[0] if seen_pos else 1
        derived_off = (seen_pos[0] - cps_shared[0]) if (seen_pos and cps_shared) else 0
        cps = sorted(int(r["CO_POSICAO"]) for r in sub)
        if area == "LC":
            # LC needs a STRUCTURAL test, not a range test. Its CO_POSICAO always
            # starts at 1 under both conventions, so "cps[0] >= printed_lo" was
            # unconditionally True and the per-area branch below was unreachable
            # -- 2017 LC reproduced the +5 shift exactly. The real difference:
            # continuous LC numbers 1-45 and DUPLICATES 1-5, one row per
            # language; per-area LC numbers 1-50 with no duplicates (1-5 English,
            # 6-10 Spanish, 11-50 shared). Confirmed against INEP's printed keys:
            # cp = p + 5 gives 40/40 on 2017 LC, cp = p gives 7/40 (chance).
            continuous = len(cps) != len(set(cps))
        else:
            continuous = bool(cps) and cps[0] >= printed_lo
        lut = {}
        for r in sub:
            cp = int(r["CO_POSICAO"])
            ling = (r.get("TP_LINGUA") or "").strip()
            if continuous:
                # derived_off is 0 for a genuinely continuous year, so this
                # reproduces every year that already passed. It is non-zero
                # only when CO_POSICAO and the PRINTED order disagree: 2016
                # numbers CO_POSICAO in INEP's canonical LC/CH/CN/MT order
                # (LC 1-45, CH 46-90, CN 91-135, MT 136-180) while the booklet
                # prints CH/CN on day 1 and LC/MT on day 2. Before this, the
                # range test `cps[0] >= printed_lo` was trivially true for
                # 2016 CH (46 >= 1), so the offset branch below was
                # UNREACHABLE and CH/CN/LC matched 0 of 140 items -- the same
                # unreachable-branch bug documented for LC above.
                key_pos, key_ling = cp + derived_off, ling
            elif area == "LC":
                # per-area LC: 1-5 English, 6-10 Spanish, 11-50 shared, against
                # printed 1-5 / 1-5 / 6-45
                if ling == "0":
                    key_pos, key_ling = cp, "0"
                elif ling == "1":
                    key_pos, key_ling = cp - 5, "1"
                else:
                    key_pos, key_ling = cp - 5, ""
            else:
                # measured offset; equals 0 when continuous and printed_lo-1
                # when per-area, and expresses 2016's mixed case too
                key_pos, key_ling = cp + derived_off, ling
            lut[(key_pos, key_ling)] = r
        conv = "continuous" if continuous else "per_area"
        if continuous and derived_off:
            conv = f"continuous{derived_off:+d}"
        report.setdefault("position_convention", {})[area] = conv
        report.setdefault("derived_offset", {})[area] = derived_off
        pub = set(info["published_items"])
        table = f"enem_{year}_1mil_{area.lower()}"
        out, seen = [], set()
        for (ar, pos, ling), opts in sorted(by_item.items()):
            if ar != area:
                continue
            rec = lut.get((pos, ling))
            if rec is None:
                report["unmatched"].append({"area": area, "position": pos, "tp_lingua": ling})
                continue
            item, key = rec["CO_ITEM"], (rec["TX_GABARITO"] or "").strip()
            if item not in pub:
                continue                      # accessibility-only: R2, do not ship
            if key not in KEYS:               # R3: no scorable key
                report["no_key_skipped"].setdefault(area, []).append(item)
                continue
            if has_aban and (rec.get("IN_ITEM_ABAN") or "0").strip() not in ("0", ""):
                report["aban_kept"].setdefault(area, []).append(
                    {"item": item, "motivo": rec.get("TX_MOTIVO_ABAN", "")})
            seen.add(item)
            stem = opts[0]["stem"]
            if not any((o["option_text"] or "").strip() for o in opts):
                report["empty_options"].append({"area": area, "item": item})
            for o in sorted(opts, key=lambda x: x["option_letter"]):
                letter = o["option_letter"]
                out.append({
                    "table": table,
                    "section_id": f"{table}_{shared.get((area, pos), (1, ''))[0]}",
                    "item": item,
                    "instrument": f"ENEM {year} - {area}",
                    "instructions": cover.get(area, ""),
                    "section_prompt": shared.get((area, pos), (None, ""))[1],
                    "item_text": stem, "correct_response": key,
                    "option_text": o["option_text"], "resp": 1 if letter == key else 0,
                    "item_text_translated": "", "option_text_translated": "",
                    "instructions_translated": "", "section_prompt_translated": "",
                    "language": "Portuguese", "resp_raw": letter})
        report["needs_standard"][area] = sorted(pub - seen)
        p = os.path.join(a.out_dir, f"{table}__items.csv")
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, SCHEMA); w.writeheader(); w.writerows(out)
        print(f"  {table}: {len(seen)} of {len(pub)} published items, {len(out)} rows -> {p}")

    print("\n  --- report (nothing here is resolved automatically) ---")
    pc = report.get("position_convention", {})
    if pc:
        print(f"    position convention detected: {pc}")
        print("    CONFIRM IT with 16_verify_gabarito.py before shipping -- a wrong")
        print("    convention attaches real text to the wrong item and every count still agrees")
    for area, miss in report["needs_standard"].items():
        if miss:
            print(f"    {area}: {len(miss)} item(s) need the standard booklet: {miss}")
    for area, v in report["aban_kept"].items():
        for x in v:
            print(f"    {area}: item {x['item']} IN_ITEM_ABAN, valid key -- KEEP and disclose ({x['motivo'][:44]})")
    for area, v in report["no_key_skipped"].items():
        print(f"    {area}: {len(v)} item(s) with no scorable key, not shipped: {v}")
    if report["unmatched"]:
        print(f"    {len(report['unmatched'])} parsed position(s) matched no ITENS_PROVA row: {report['unmatched'][:6]}")
    if report["empty_options"]:
        print(f"    {len(report['empty_options'])} item(s) parsed with empty options (R5 candidates): {report['empty_options'][:6]}")
    json.dump(report, open(os.path.join(a.out_dir, "join_report.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
