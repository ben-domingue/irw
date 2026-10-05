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
    dict(year="2013", item="43855", column="item_text", letter=None,
         old="Considere 3 como valor aproximado para p.",
         new="Considere 3 como valor aproximado para \u03c0.",
         why="SymbolMT CID 83 is pi; INEP's own /ToUnicode declares it U+0070. "
             "Caderno7_Azul_Dom p25. Whole-sentence anchor: 5 fields, 1 item, "
             "where the loose 'aproximado para p' matches 25 fields in 5 items."),

    # ---- the review's `number` class: 23 SPURIOUS carets --------------
    #
    # None of these glyphs is a script. Every one measures 100.00% of its
    # line's body size with a rise of exactly +0.000pt -- they are ordinary
    # text. The carets leaked in from 48_mark_scripts.py's option-letter
    # RETRY, which strips the letter and then matches without the
    # start-boundary guard the primary path uses. Two genuine scripts in the
    # AZUL gap-fill booklets did the damage: 2017 d2 p18's options "D 6^4"
    # and "E 4^6" strip to the bare anchors "6" and "4", and 2020 d2 p7's
    # "A 10^0" strips to "10". Those match inside the year 1964, a tooth
    # count of 46, "a cada 100 minutos", "o artigo 100" and the keyed
    # "11 460".
    #
    # WHY A TABLE AND NOT A FIX TO THE RETRY. Tightening it was tried and
    # reverted. A minimum anchor length cannot work: the retry legitimately
    # fires on 1-character anchors when the whole option cell is short --
    # requiring 4+ characters deleted the genuine "H_2", "Cl_2", "CO_2" of
    # 2020 CN 76371, the "6H_2O" of 111722 and the "62^6" of 2013 MT 31416.
    # Requiring the match to start at the cell head fails too: 111722's
    # correct marker sits mid-stem. Short anchors are both necessary and
    # harmful, and nothing cheap separates them.
    #
    # EVERY ENTRY IS ROW-SCOPED on (year, item, column, letter) and that is
    # load-bearing, not tidiness: 84444's "10^0" occurs in 14 distinct items
    # corpus-wide, one of which -- 2013 CN 38783 option E, "2 x 10^0 T." --
    # is a GENUINE 10^0. An unscoped replace would corrupt it.
    dict(year='2017', item='62247', column='option_text', letter='C',
         old='4^60.',
         new='460.',
         why="Printed option C of 2017 CN is the single plain span '11 460.' at 100.00% of the 9.75pt body with 0.000pt rise; the caret came from a genuine 4⁶ in option E of 2017 MT Questao 143 (AZUL d2 p18) whose anchor collapsed to the bare digits '46'. ENEM_2017_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p5; span 100.00% of body size, rise +0.000pt"),
    dict(year='2017', item='78598', column='option_text', letter='D',
         old='6^40.',
         new='640.',
         why="Printed option D is the plain span '640.' at 100.00% / 0.000pt rise; the caret came from the genuine 6⁴ in option D of AZUL d2 p18 Questao 143, anchored on the bare digits '64'. ENEM_2017_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p8; span 100.00% of body size, rise +0.000pt"),
    dict(year='2017', item='88873', column='option_text', letter='D',
         old='−6^4.',
         new='−64.',
         why="Printed option D is the plain span '64.' at 100.00% / 0.000pt rise (the minus is a separate 100%-size SymbolMT span), so −64 is an integer, not −6⁴. ENEM_2017_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p10; span 100.00% of body size, rise +0.000pt"),
    dict(year='2017', item='82891', column='item_text', letter=None,
         old='196^4,',
         new='1964,',
         why="The printed line sets ', encenada em 1964, ' as one 100.00%-size ArialMT span with 0.000pt rise — 1964 is the year the play was staged, not 196⁴. ENEM_2017_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf p11; span 100.00% of body size, rise +0.000pt"),
    dict(year='2017', item='38563', column='option_text', letter='A',
         old='6^4',
         new='64',
         why="Printed option A is the plain span '64' at 100.00% / 0.000pt rise; this item's answer is the integer 64, while the genuine 6⁴ sits in a different item (AZUL d2 p18 Questao 143 option D). ANCHOR NOT CORPUS-UNIQUE: the whole shipped cell is '6^4', so no longer anchor exists; it must be applied row-scoped (item+column+option_letter). ENEM_2017_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p17; span 100.00% of body size, rise +0.000pt"),
    dict(year='2017', item='81410', column='item_text', letter=None,
         old='4^6;',
         new='46;',
         why="The whole line including 'coroa: 46;' is one 100.00%-size span with 0.000pt rise — 46 is a tooth count, not 4⁶. ENEM_2017_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p26; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='17936', column='item_text', letter=None,
         old='cada 10^0',
         new='cada 100',
         why="The entire line 'de agua. Observou-se que, a cada 100 minutos de ' is a single 100.00%-size span with 0.000pt rise — the reaction was sampled every 100 minutes. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p8; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='49867', column='item_text', letter=None,
         old='10^0 metros',
         new='100 metros',
         why="The entire line 'estiver a 100 metros de cruza-los, ...' is one 100.00%-size span with 0.000pt rise — the distance is 100 metres. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p11; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='84444', column='option_text', letter='A',
         old='10^0',
         new='100',
         why="This item is AZUL d2 p7 Questao 106 (gap-filled from the standard booklet); its option A prints as the single span ' 100' at 100.00% / 0.000pt rise, while the GENUINE 10⁰ that produced the caret is option A of Questao 107 lower on the very same page at 59.79% / +4.604pt. ANCHOR NOT CORPUS-UNIQUE: the whole shipped cell is '10^0', so no longer anchor exists; it must be applied row-scoped (item+column+option_letter). ENEM_2020_P1_CAD_07_DIA_2_AZUL.pdf p7; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='112151', column='item_text', letter=None,
         old='10^0,',
         new='100,',
         why="The entire line 'das atribuicoes que lhe confere o artigo 100, incisos Setimo ' is one 100.00%-size span with 0.000pt rise — article 100 of a decree. ENEM_2020_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf p12; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='10660', column='item_text', letter=None,
         old='\n10^0',
         new='\n100',
         why="The entire line '100 quilometros rodados, e o tanque da moto tem ' is one 100.00%-size span with 0.000pt rise — 100 km per 5 litres. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p16; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='15897', column='item_text', letter=None,
         old='que em 10^0',
         new='que em 100',
         why="The entire line 'e, apos analise laboratorial, foi identificado que em 100 ' is one 100.00%-size span with 0.000pt rise — 100 of the 200 samples. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p18; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='15897', column='option_text', letter='E',
         old='10^0.',
         new='100.',
         why="Printed option E is 'E \\t 100.' with the digits in a 100.00%-size span at 0.000pt rise — 100 samples, not 10⁰. ANCHOR NOT CORPUS-UNIQUE: the whole shipped cell is '10^0.', so no longer anchor exists; it must be applied row-scoped (item+column+option_letter). ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p18; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='32975', column='option_text', letter='B',
         old='para 10^0',
         new='para 100',
         why="KEYED option B prints as 'B \\t 1 para 100' with the digits in a 100.00%-size span at 0.000pt rise — the scale is 1:100, and the caret made the key read 1:10⁰ = 1:1. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p20; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='32975', column='option_text', letter='E',
         old='10^0 000',
         new='100 000',
         why="Printed option E is 'E \\t 1 para 100 000', digits in a 100.00%-size span at 0.000pt rise — scale 1:100 000. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p20; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='55387', column='option_text', letter='A',
         old='a 10^0.',
         new='a 100.',
         why="Printed option A is 'A \\t Um meio elevado a 100.' in a 100.00%-size span at 0.000pt rise — the exponent is already spelled out in words ('elevado a'), so the digits are the literal 100. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p17; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='59546', column='item_text', letter=None,
         old='1 10^0',
         new='1 100',
         why="The entire line 'Dia 1: 800 pecas; Dia 2: 1 000 pecas; Dia 3: 1 100 ' is one 100.00%-size span with 0.000pt rise — 1 100 pieces. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p20; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='63324', column='item_text', letter=None,
         old='com 10^0',
         new='com 100',
         why="The entire line 'um carro de Formula 1, com 100 micrometros de ' is one 100.00%-size span with 0.000pt rise — 100 micrometres. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p26; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='7633', column='item_text', letter=None,
         old='tem 10^0',
         new='tem 100',
         why="The entire line 'tem 100 centimetros de altura, incluida sua base.' is one 100.00%-size span with 0.000pt rise — 100 cm tall. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p21; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='86282', column='option_text', letter='A',
         old='vezes 10^0',
         new='vezes 100',
         why="Printed option A is 'A \\t X vezes 100' with ' vezes 100' in a 100.00%-size span at 0.000pt rise — this LEDOR item spells its operations out in words, so the digits are the literal 100. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p22; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='86282', column='option_text', letter='B',
         old='por 10^0',
         new='por 100',
         why="Printed option B is 'B \\t X dividido por 100' with ' dividido por 100' in a 100.00%-size span at 0.000pt rise. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p22; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='86282', column='option_text', letter='C',
         old='10^0 dividido',
         new='100 dividido',
         why="KEYED option C prints as 'C \\t 100 dividido por X' with '\\t 100 dividido por ' in a 100.00%-size span at 0.000pt rise — the caret made the key read 10⁰/X = 1/X. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p22; span 100.00% of body size, rise +0.000pt"),
    dict(year='2020', item='86803', column='item_text', letter=None,
         old='Quatro: 10^0',
         new='Quatro: 100',
         why="The entire line 'Perfume Tres: 150 reais; Perfume Quatro: 100 ' is one 100.00%-size span with 0.000pt rise — a price of 100 reais. ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf p18; span 100.00% of body size, rise +0.000pt"),
]

# (E) THE 2022 TAB. INEP's own /ToUnicode declares ArialMT and SymbolMT CID 3
# as U+0009 instead of U+0020, so 2022 ships 73 133 literal TAB characters --
# and only 2022; no other year has one. They are word separators:
#     "vacina\tcontra\ta\tdoença\tusando\tuma"
# Every one is a SINGLE tab (no runs), and the neighbour census is
#     ch TAB ch   54 034      ch TAB NL    5 033
#     ch TAB SP   14 034      SP TAB NL/ch    32
# so a naive TAB -> space would leave 14 066 DOUBLE spaces. These three
# ordered rules give exactly one space per tab instead. Collapsing whitespace
# generally is NOT an option: the corpus has intentional multi-space runs,
# including 2015 CN 25964's "ΔH  =   −18,8 kJ/g" labels.
#
# Nothing in the pipeline depends on a literal tab: the only \t in any pass is
# VECTOR_ACCENT above, whose [ \t] accepts either.
TABS = [(" \t", " "), ("\t ", " "), ("\t", " ")]

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


def fix(v, year=None, item=None, column=None, letter=None):
    if not v:
        return v, collections.Counter()
    n = collections.Counter()
    if "\t" in v:
        k = v.count("\t")
        for a, b in TABS:
            v = v.replace(a, b)
        n["TAB -> space (2022 CID 3)"] += k
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
    for p in PATCH:
        if year != p["year"] or item != p["item"] or column != p["column"]:
            continue
        if p["letter"] is not None and (letter or "").strip() != p["letter"]:
            continue
        if p["old"] not in v:
            continue
        n["patch %s %s" % (p["year"], p["item"])] += v.count(p["old"])
        v = v.replace(p["old"], p["new"])
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
                nv, n = fix(r[c], year=year, item=r.get("item"),
                            column=c, letter=r.get("resp_raw"))
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
