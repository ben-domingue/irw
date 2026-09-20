#!/usr/bin/env python3
"""Replace SymbolMT /gNNN tokens in parsed item text with their characters.

2022's CN and MT booklets set some notation in simple Type1 SymbolMT subsets
whose /Encoding -> /Differences names glyphs opaquely (/g167, with no semantic
name anywhere in the file), and with no /ToUnicode. So no extractor can resolve
them and 17_decode_2018.py's repair_pdf() does not apply -- that handles
Type0/Identity-H, a different mechanism.

THE RULE, derived and cross-validated by the 2018 decoder work:
    NNN is the glyph id, and over the Adobe Symbol encoding
        code = GID + 29   for GID 3-97
        code = GID + 63   for GID >= 98
It reproduces all 13 SymbolMT entries derived independently for 2018 from
outline evidence, 13/13 -- two unrelated derivations agreeing. The clincher is
that g167/168/169 and g183/184/185 come out as parenlefttp/ex/bt and
parenrighttp/ex/bt, the two three-piece triples that typeset a large

# Confidence notes, so a later reader knows what each entry rests on:
#   code 43 (GID 14) = "+" is contextually PROVEN. 2022 MT 89637's options
#     extract as '1 46 2 46 45/g14/g117', and the accessibility booklet words the
#     same option independently as "...denominador 46 MAIS fração de numerador 2
#     e denominador (46 VEZES 45)". So /g14 is + and /g117 is x (code 180).
#   code 215 (GID 152) = dotmath rests on the Adobe Symbol encoding and the 2018
#     evidence of Fe2O3.H2O, NOT on 2022 context -- its only 2022 occurrence is
#     inside a garbled table header. Weakest entry here; check against a
#     rendered page if it matters.
parenthesis, and they appear together in the same /Differences arrays.

Only GIDs with evidence are mapped. An unmapped GID is REPORTED and left as its
marker, never guessed: a plausible-looking symbol is exactly the failure this
project keeps finding.

Usage: python3 23_decode_symbolmt.py <items.csv> [<items.csv> ...] [--apply]
       (without --apply it only reports)
"""
import csv, re, sys

TOKEN = re.compile(r"/g(\d+)")

# Adobe Symbol code -> character, for the codes the rule resolves to. Each entry
# is here because a GID observed in a real ENEM booklet maps onto it.
SYMBOL = {
    32: " ", 43: "+", 40: "(", 41: ")", 45: "−", 46: ".", 48: "0", 49: "1",
    60: "<", 61: "=", 62: ">", 68: "Δ", 70: "ƒ", 80: "Π",
    112: "π", 113: "θ", 163: "≤", 165: "∞", 166: "ƒ", 174: "→", 176: "°",
    180: "×", 179: "≥", 206: "∈",
    230: "⎛", 231: "⎜", 232: "⎝",   # parenlefttp / ex / bt
    246: "⎞", 247: "⎟", 248: "⎠",   # parenrighttp / ex / bt
    215: "⋅",                                # dotmath (see note above)
}


def gid_to_code(gid):
    if 3 <= gid <= 97:
        return gid + 29
    if gid >= 98:
        return gid + 63
    return None


def decode(text, unknown):
    def sub(m):
        gid = int(m.group(1))
        code = gid_to_code(gid)
        ch = SYMBOL.get(code) if code else None
        if ch is None:
            unknown[gid] = unknown.get(gid, 0) + 1
            return m.group(0)
        return ch
    return TOKEN.sub(sub, text)


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply_it = "--apply" in sys.argv
    for f in files:
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        if not rows:
            continue
        unknown, changed = {}, 0
        for r in rows:
            for col in ("item_text", "option_text", "section_prompt", "instructions"):
                if col in r and r[col] and TOKEN.search(r[col]):
                    new = decode(r[col], unknown)
                    if new != r[col]:
                        r[col] = new; changed += 1
        left = sum(len(TOKEN.findall(r.get(c) or "")) for r in rows
                   for c in ("item_text", "option_text", "section_prompt", "instructions"))
        print(f"  {f.split('/')[-1]:34} fields decoded={changed:>4} tokens left={left:>4}"
              + (f"  UNMAPPED GIDs {sorted(unknown)}" if unknown else ""))
        if apply_it and changed:
            with open(f, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
