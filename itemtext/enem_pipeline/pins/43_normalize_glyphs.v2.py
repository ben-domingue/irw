#!/usr/bin/env python3
"""Repair source-declared wrong glyphs, and normalise typographic variants.

TWO DIFFERENT THINGS, kept apart on purpose.

(A) WRONG GLYPHS THE SOURCE ITSELF DECLARES. Verified by reading the ORIGINAL,
    unrepaired INEP PDF: the bad character is already there, so this is a
    defect in INEP's own /ToUnicode and not in our decoding. We are faithfully
    reproducing a broken table, which is worse than useless to a reader.
      U+021C YOGH        -> lambda   2015 CN 82658, "comprimento de onda (λ)",
                                     and options "λ/4", "λ/2", "3λ/4"
      U+0138 KRA         -> the left half of the equilibrium arrow. 2016 CN
                           40112 prints "C6H5OH + H2O ⇌ C6H5O− + H3O+"; the
                           original reads "ĺĸ", two halves, and the repair
                           already resolved "ĺ" to "→". Both halves together
                           are one ⇌, so the pair "→ĸ" collapses to "⇌".
    Both were found by Ben on PR #2226 and confirmed against the source.

(B) ADOBE SYMBOL PRIVATE-USE CODES. U+F0XX is the Symbol font's character at
    code 0xXX -- a documented spec mapping, not an inference. Corroborated by
    context in every case that carries meaning:
      U+F02B -> "+"   2022 CN 44969  "ONa NaO + 2 NaOH → 2 H2O"
      U+F02D -> "−"   2022 CN 44969  "150 g mol−1"
      U+F0DE -> "⇒"   2022 MT 63646
      U+F072 -> a VECTOR ARROW over the label on the NEXT LINE, not "ρ".
                      2022 CN 85445. This entry read "ρ" on the strength of
                      the Adobe Symbol code page and was flagged in place as
                      the weakest in the map. Measurement settles it the other
                      way, twice over: the font is MT-Extra, not Symbol (all
                      21 spans on acc_d2 p14), so that code page never
                      governed it; and every span sits 4.1-5.0pt ABOVE a base
                      letter with overlapping x (F, P, N, f), the region
                      rendering as a free-body diagram labelled N, f_e and P
                      each under an arrow.
                      It is a diacritic, and not droppable: the vector label
                      carries the vector/magnitude distinction the item is
                      about, and option E is the keyed one. Written as U+20D7
                      COMBINING RIGHT ARROW ABOVE, which must FOLLOW its base
                      while the glyph PRECEDES it in reading order -- so this
                      is a reorder and is handled positionally below, not by
                      the one-for-one map. First combining mark in the ENEM
                      corpus (ruled 2026-10-02).

(C) TYPOGRAPHIC NORMALISATION. Same character, different code point. The
    ligatures are the big one: 2,543 occurrences and ONLY in 2013 and 2017, so
    a search for "significa" misses those years while matching every other.
    (Ben reported the ligatures as 2017-only; they are in 2013 as well.)

Usage:  python3 43_normalize_glyphs.py --items-dir <dir> [--apply]
"""
import argparse, csv, glob, os, re, sys, collections

SCHEMA = ["table","section_id","item","instrument","instructions","section_prompt",
          "item_text","correct_response","option_text","resp","item_text_translated",
          "option_text_translated","instructions_translated","section_prompt_translated",
          "language","resp_raw"]

# (A) + (B): wrong glyphs, replaced one for one
WRONG = {
    "Ȝ": "λ",   # yogh   -> lambda
    "": "+",        # Symbol 0x2B
    "": "−",   # Symbol 0x2D
    "": "⇒",   # Symbol 0xDE
}
# the equilibrium arrow is a PAIR, so it is handled before the single-char map
PAIRS = [("→ĸ", "⇌"), ("ĸ", "⇌")]

# U+F072 is a vector arrow set ABOVE the label on the NEXT line:
#     CM / <F072> / F / <F072> / P / <F072> / f_e / <F072> / N
# A Unicode combining mark follows its base, so the pair becomes base+U+20D7.
# The arrow attaches to the BASE LETTER, before any subscript marker, because
# that is where it is printed: "f_e" becomes "f" + arrow + "_e".
VECTOR_ACCENT = re.compile("\uf072[ \\t]*\\n[ \\t]*([A-Za-z\\u00c0-\\u00ff])")

# (D) A WRONG GLYPH THAT ARRIVES AS ORDINARY ASCII, so no map can see it.
#
# 2013 MT 43855 prints "Considere pi como valor aproximado para pi." -- the
# second symbol is SymbolMT, Type0/Identity-H, and the PDF carries its own
# /ToUnicode declaring
#       <0053> <0070>          i.e. CID 83 -> U+0070 "p"
# CID 83 is pi: the glyph order (code = GID + 29) is the rule 17_decode_2018.py
# derived and cross-validated, and its own SYMBOL_CID[83] = "pi", pinned by
# 2018's "Considere o valor de pi com aproximacao". So INEP declared the wrong
# character and every extractor faithfully reports "p".
#
# WHY A PATCH AND NOT A PDF-LEVEL OVERRIDE. 17_decode_2018.py repair_pdf()
# INJECTS a missing CMap and explicitly declines a font that already has one
# ("already had ToUnicode"), so it would have to learn to OVERRIDE. Comparing
# every Identity-H /ToUnicode against the family tables across all 36 booklets
# turns up 277 disagreements -- CID 3 tab-vs-space (the separate `tabs` class,
# 159 findings), CID 16 hyphen-vs-minus, the fi/fl ligatures that NORM already
# folds, and ~240 in 2020 whose CMaps are code-identity so the comparison does
# not even apply. An unscoped override would garble 2020 wholesale. Scoped to
# {SymbolMT, CID 83} it has exactly ONE match in the corpus -- this item -- so
# a sentence-anchored patch has the same blast radius at a fraction of the risk.
#
# The anchor is the WHOLE sentence, measured: it matches 5 fields in 1 item,
# while the loose "aproximado para p" matches 25 fields across 5 items
# (43855, 82446, 84940, 125957, 44510). pi already ships in 10 items, including
# 2016 MT 11472's identically-shaped "Utilize 3 como aproximacao para pi."
PATCH = [
    ("2013", "43855",
     "Considere 3 como valor aproximado para p.",
     "Considere 3 como valor aproximado para \u03c0."),
]

# (C) typographic normalisation
NORM = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff",
    "ﬃ": "ffi", "ﬄ": "ffl",
    "Ω": "Ω",   # OHM SIGN      -> GREEK CAPITAL OMEGA (Unicode advises)
    "∆": "Δ",   # INCREMENT     -> GREEK CAPITAL DELTA
    "µ": "μ",   # MICRO SIGN    -> GREEK SMALL MU
    "ʼ": "’",   # MODIFIER LETTER APOSTROPHE
    "ꞌ": "’",   # SALTILLO -- "Didnꞌt" in a 2019 LC song lyric
    "‛": "‘",   # SINGLE HIGH-REVERSED-9
    " ": " ",        # HAIR SPACE
}

COLS = ("item_text", "option_text", "section_prompt", "instructions")


def fix(v, year=None, item=None):
    if not v:
        return v, collections.Counter()
    n = collections.Counter()
    for a, b in PAIRS:
        if a in v:
            n["pair " + a] += v.count(a); v = v.replace(a, b)
    if "\uf072" in v:
        v, k = VECTOR_ACCENT.subn(lambda m: m.group(1) + "\u20d7", v)
        n["U+F072 -> base+U+20D7"] += k
        if "\uf072" in v:
            # An accent with no label on the next line is not a case this
            # rule understands. Report it rather than shipping a private-use
            # glyph or guessing at a base.
            n["UNPLACED U+F072 (reported, not rewritten)"] += v.count("\uf072")
    for a, b in {**WRONG, **NORM}.items():
        if a in v:
            n[a] += v.count(a); v = v.replace(a, b)
    for yy, it, oldv, newv in PATCH:
        if year == yy and item == it and oldv in v:
            n["patch %s %s" % (yy, it)] += v.count(oldv)
            v = v.replace(oldv, newv)
    return v, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    grand = collections.Counter(); files = 0
    for p in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        # PATCH entries are keyed on (year, item); the year is in the filename,
        # enem_<YYYY>_1mil_<area>__items.csv, which is the same name the batch
        # directory ships. Nothing else in this pass is year-aware.
        ym = re.search(r"enem_(\d{4})_", os.path.basename(p))
        year = ym.group(1) if ym else None
        touched = False
        for r in rows:
            for c in COLS:
                if c not in r:
                    continue
                nv, n = fix(r[c], year=year, item=r.get("item"))
                if n:
                    r[c] = nv; grand.update(n); touched = True
        if touched:
            files += 1
            if a.apply:
                with open(p, "w", newline="", encoding="utf-8") as fh:
                    w = csv.DictWriter(fh, SCHEMA); w.writeheader()
                    for r in rows:
                        w.writerow({k: r.get(k, "") for k in SCHEMA})
    if grand:
        for k, v in grand.most_common():
            lbl = k if len(k) != 1 else f"U+{ord(k):04X} {k!r}"
            print(f"    {lbl:22s} x{v}")
    print(f"  {'applied to' if a.apply else 'WOULD touch'} {files} file(s); "
          f"{sum(grand.values())} substitution(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
