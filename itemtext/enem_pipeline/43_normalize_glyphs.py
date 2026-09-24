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
      U+F072 -> "ρ"   2022 CN 85445. WEAKEST ENTRY: the spec says Symbol 0x72
                      is rho, but it sits among figure labels (CM, F, P, fe, N)
                      where INEP may have meant a vector arrow. The spec
                      reading ships; the ambiguity is disclosed.

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
    "": "ρ",   # Symbol 0x72 (weakest; see docstring)
}
# the equilibrium arrow is a PAIR, so it is handled before the single-char map
PAIRS = [("→ĸ", "⇌"), ("ĸ", "⇌")]

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


def fix(v):
    if not v:
        return v, collections.Counter()
    n = collections.Counter()
    for a, b in PAIRS:
        if a in v:
            n["pair " + a] += v.count(a); v = v.replace(a, b)
    for a, b in {**WRONG, **NORM}.items():
        if a in v:
            n[a] += v.count(a); v = v.replace(a, b)
    return v, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    grand = collections.Counter(); files = 0
    for p in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        touched = False
        for r in rows:
            for c in COLS:
                if c not in r:
                    continue
                nv, n = fix(r[c])
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
            lbl = k if k.startswith("pair") else f"U+{ord(k):04X} {k!r}"
            print(f"    {lbl:22s} x{v}")
    print(f"  {'applied to' if a.apply else 'WOULD touch'} {files} file(s); "
          f"{sum(grand.values())} substitution(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
