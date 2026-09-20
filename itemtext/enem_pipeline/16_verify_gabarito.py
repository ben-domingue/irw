#!/usr/bin/env python3
"""Verify a year's position -> CO_ITEM mapping against INEP's PRINTED answer keys.

WHY THIS EXISTS. validate_items.R compares item SETS and resp SETS. Neither can
detect a position offset: if every printed question's text is attached to the
item five positions away, the set is still complete and resp is still {0,1}, so
both checks pass. That is not hypothetical -- 2017 LC shifted by +5, shipped 40
of 50 items and reported "PASS: resp sets match exactly" with every stem on the
wrong item code.

The independent check is INEP's own printed gabarito. It gives
printed position -> correct letter. ITENS_PROVA gives CO_ITEM -> TX_GABARITO. So
for a candidate mapping, agreement across all ~180 positions is strong evidence
the mapping is right, and disagreement at chance level proves it is wrong. The
letters are effectively a random 5-way string, so 175/175 agreement cannot
happen by accident.

Usage:
  python3 16_verify_gabarito.py --year 2019 --gabarito <gab1.pdf> [<gab2.pdf>] \
      [--mapping continuous|per_area]
"""
import argparse, csv, glob, json, logging, os, re, sys, warnings
logging.disable(logging.CRITICAL); warnings.filterwarnings("ignore")
from pypdf import PdfReader

ENEM = os.path.expanduser("~/enem")
KEYS = set("ABCDE")
# Printed position ranges by area. NOT constant across years: 2017+ print
# LC first, 2013-2016 print CH first. Select with --printed-order, and the
# default stays the 2017+ layout that most years use.
PRINTED_ORDERS = {
    "lc_first": {"LC": (1, 45), "CH": (46, 90), "CN": (91, 135), "MT": (136, 180)},
    "ch_first": {"CH": (1, 45), "CN": (46, 90), "LC": (91, 135), "MT": (136, 180)},
}
PRINTED = PRINTED_ORDERS["lc_first"]


def gab_pairs(pdfs):
    """printed position -> letter, from 'NN X' lines in the gabarito."""
    out = {}
    for p in pdfs:
        txt = "\n".join((pg.extract_text() or "") for pg in PdfReader(p).pages)
        for m in re.finditer(r"^\s*(\d{1,3})\s+([A-E])\s*$", txt, re.M):
            pos, letter = int(m.group(1)), m.group(2)
            if 1 <= pos <= 180:
                out[pos] = letter
        # The LC language block prints TWO keys per row, "INGLÊS ESPANHOL":
        # "1 D E" means English=D, Spanish=E. The single-letter pattern above
        # skips those rows entirely, which is why only 175 of 180 positions were
        # ever compared and LC 1-5 went unchecked.
        for m in re.finditer(r"^\s*(\d{1,2})\s+([A-E])\s+([A-E])\s*$", txt, re.M):
            pos = int(m.group(1))
            if 1 <= pos <= 5:
                out[("LC0", pos)] = m.group(2)
                out[("LC1", pos)] = m.group(3)
    return out


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
    ap.add_argument("--gabarito", nargs="+", required=True)
    ap.add_argument("--colour", default=None, help="TX_COR of the gabarito's booklet")
    ap.add_argument("--manifest", default=f"{ENEM}/itemtext_run/allyears/manifest.json")
    ap.add_argument("--printed-order", choices=sorted(PRINTED_ORDERS), default="lc_first",
                    help="lc_first for 2017+, ch_first for 2013-2016")
    a = ap.parse_args()
    year = a.year
    man = json.load(open(a.manifest))[str(year)]
    sc = set(man["standard_prova_codes"])
    rows = itens(year)
    global PRINTED
    PRINTED = PRINTED_ORDERS[a.printed_order]
    gab = gab_pairs(a.gabarito)
    print(f"  gabarito: {len(gab)} printed position->letter pairs")

    # which CO_PROVA does this gabarito belong to? pick the standard code per area
    # whose TX_COR matches, or try every standard code and report the best
    results = {}
    for mapping in ("continuous", "per_area"):
        agree = total = 0
        detail = {}
        for area, (lo, hi) in PRINTED.items():
            cands = {r["CO_PROVA"] for r in rows if r["CO_PROVA"] in sc and r["SG_AREA"] == area
                     and (a.colour is None or (r.get("TX_COR") or "").upper() == a.colour.upper())}
            best = (0, 0, None)
            for prova in cands:
                sub = [r for r in rows if r["CO_PROVA"] == prova]
                lut = {}
                for r in sub:
                    cp = int(r["CO_POSICAO"])
                    ling = (r.get("TP_LINGUA") or "").strip()
                    if mapping == "continuous":
                        key = cp
                    elif area == "LC":
                        # per-area LC: 1-5 EN, 6-10 ES, 11-50 shared, against
                        # printed 1-5 / 1-5 / 6-45
                        key = cp if ling == "0" else cp - 5
                    else:
                        key = cp + lo - 1
                    lut.setdefault(key, []).append(r["TX_GABARITO"])
                ok = n = 0
                for pos in range(lo, hi + 1):
                    if pos not in gab or pos not in lut:
                        continue
                    n += 1
                    if gab[pos] in lut[pos]:
                        ok += 1
                if n and ok > best[0]:
                    best = (ok, n, prova)
            detail[area] = best
            agree += best[0]; total += best[1]
        # LC language block: the printed rows give BOTH keys ("1 D E"), so
        # compare them against TP_LINGUA 0 and 1 explicitly. Collected but never
        # compared until now, since the loop above iterates integer positions.
        lc_ok = lc_n = 0
        lc_cands = {r["CO_PROVA"] for r in rows if r["CO_PROVA"] in sc and r["SG_AREA"] == "LC"
                    and (a.colour is None or (r.get("TX_COR") or "").upper() == a.colour.upper())}
        for prova in lc_cands:
            for r in rows:
                if r["CO_PROVA"] != prova:
                    continue
                ling = (r.get("TP_LINGUA") or "").strip()
                if ling not in ("0", "1"):
                    continue
                cp = int(r["CO_POSICAO"])
                printed = cp if (mapping == "continuous" or ling == "0") else cp - 5
                want = gab.get((f"LC{ling}", printed))
                if want is None:
                    continue
                lc_n += 1
                if r["TX_GABARITO"] == want:
                    lc_ok += 1
            if lc_n:
                break
        if lc_n:
            print(f"      LC language block: {lc_ok}/{lc_n} (printed two-column keys)")
            agree += lc_ok; total += lc_n
        results[mapping] = (agree, total, detail)
        pct = 100 * agree / total if total else 0
        print(f"  mapping={mapping:<11} {agree}/{total} keys agree ({pct:.1f}%)")
        for area, (ok, n, prova) in detail.items():
            print(f"      {area}: {ok}/{n} at CO_PROVA {prova}")

    best = max(results, key=lambda k: (results[k][1] and results[k][0] / results[k][1]))
    ok, total, detail = results[best]
    untested = [ar for ar, (o, n, pv) in detail.items() if n == 0]
    print(f"\n  VERDICT: '{best}' fits best at {ok}/{total}")
    if untested:
        print(f"  !! NOT VERIFIED: no printed positions were compared for {', '.join(untested)}.")
        print("     An area whose printed range does not overlap contributes n=0, which")
        print("     shrinks the denominator silently -- 2015 once reported 45/45 'exact'")
        print("     having tested only MT, with 135 of 180 positions never checked.")
        print("     Fix the PRINTED range for this year before trusting any figure here.")
        return 1
    if total and ok == total:
        print("  -> exact. The position convention for this year is confirmed.")
        return 0
    if total and ok / total < 0.5:
        print("  -> AT OR NEAR CHANCE. The mapping is WRONG; do not ship this year.")
        return 1
    print("  -> partial agreement: investigate before shipping.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
