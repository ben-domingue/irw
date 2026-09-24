#!/usr/bin/env python3
"""Inventory every unusual character in the shipped item text, by year.

Ben's check, generalised: rather than look for characters we already suspect,
enumerate everything outside the set Portuguese/Spanish/English exam prose
actually needs, and show where each one occurs. A wrong glyph is invisible to
every structural gate -- item_set_match stays TRUE when a minus sign decodes as
a thorn -- so this is the only class of check that can see it.
"""
import csv, collections, glob, json, os, re, sys, unicodedata

REPO = os.path.expanduser("~/irw/itemtext/itemtables")
YEARS = ["2013","2015","2016","2017","2018","2019","2020","2021","2022","2024","2025"]

# what exam prose legitimately contains
OK = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    " \n\t\r"
    ".,;:!?()[]{}\"'`/\\|-_+=*&%$#@^~<>"
    "áàâãéêíóôõúüç"
    "ÁÀÂÃÉÊÍÓÔÕÚÜÇ"
    "ñÑ¿¡"                       # Spanish
    "“”‘’–—…«»"   # punctuation
    "ºª°§·•"            # ordinals, degree, bullet
    "±×÷−≤≥≠∞∑∏∫√"
    "αβγδεθλμπρστφω"
    "ΔΩΣΠ"
    "→←↔⇌≡≈∼"
    "²³¹⁰⁴⁵⁶⁷⁸⁹⁺⁻ⁿ"
    "₀₁₂₃₄₅₆₇₈₉"
    "€£¥¢‰′″"
    "■○●─│"
)

def main():
    bad = collections.defaultdict(lambda: collections.defaultdict(list))
    per_year = collections.defaultdict(collections.Counter)
    for y in YEARS:
        for p in sorted(glob.glob(f"{REPO}/batch_enem_{y}/*__items.csv")):
            a = re.search(r"_1mil_(\w\w)__", p).group(1)
            for r in csv.DictReader(open(p, encoding="utf-8")):
                for col in ("item_text", "option_text", "section_prompt", "instructions"):
                    v = r.get(col) or ""
                    for ch in set(v):
                        if ch in OK:
                            continue
                        per_year[ch][y] += 1
                        if len(bad[ch][y]) < 2:
                            i = v.index(ch)
                            bad[ch][y].append(
                                (a.upper(), r["item"], col,
                                 re.sub(r"\s+", " ", v[max(0, i-38):i+38])))
    print(f"  {len(per_year)} distinct unexpected character(s)\n")
    print("  char        U+     name                             years (item-fields)")
    for ch in sorted(per_year, key=lambda c: -sum(per_year[c].values())):
        try: nm = unicodedata.name(ch)
        except ValueError: nm = "<unnamed>"
        tot = sum(per_year[ch].values())
        yrs = ",".join(f"{y}:{n}" for y, n in sorted(per_year[ch].items()))
        print(f"  {ch!r:10s} {ord(ch):04X}  {nm[:32]:32s} {tot:5d}  {yrs}")
    json.dump({ch: {y: v for y, v in d.items()} for ch, d in bad.items()},
              open("charaudit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n  contexts -> charaudit.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
