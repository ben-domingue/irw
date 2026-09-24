#!/usr/bin/env python3
"""Apply the two option conventions ruled by Mateus on PR #2226 (2026-09-20).

(A) DUPLICATE OPTION TEXT -> NA. Twelve items shipped two or more options with
    IDENTICAL text, because the options are DRAWINGS and what was captured is
    the labels inside them ("A B" five times, "O" five times, axis names).
    Two options of a multiple-choice item are never really identical, so the
    text is not option text at all. Ruled: NA, the same as the 37 other
    drawing items, because repeated labels are meaningless as item text.

(B) STACKED FRACTIONS -> INLINE, never NA. A fraction printed as numerator
    over denominator arrives as "17\\n70". Ruled: write it "17/70" -- it is
    perfectly expressible in plain text, so turning it into NA would destroy
    information that is right there on the page.
    Applied ONLY where every part is a clean two-line numeric: an option like
    "5!\\n2!\\n× 4!" has three parts and an operator, and joining it with "/"
    would assert a structure that is not verifiable. Those are left with their
    newlines and disclosed.

(C) THREE ITEMS transcribed from the printed page, because the extractor could
    not segment their options at all and the ruling is that fractions must not
    ship as NA. Each was read off the booklet and is quoted here so the
    transcription can be checked without rerunning anything:
      2015 MT 14712 (AZUL day 2, printed 142)  1/100 19/100 20/100 21/100 80/100
      2016 MT 60291 (AZUL day 2, printed 152)  1/96 1/64 5/24 1/4 5/12
      2016 CN 86572 (AZUL day 1, printed 59)   1 4/7 10/27 14/81 4/81

Usage:  python3 49_option_conventions.py --items-dir <dir> [--apply]
"""
import argparse, collections, csv, glob, os, re, sys

SCHEMA = ["table","section_id","item","instrument","instructions","section_prompt",
          "item_text","correct_response","option_text","resp","item_text_translated",
          "option_text_translated","instructions_translated","section_prompt_translated",
          "language","resp_raw"]

TRANSCRIBED = {
    "14712": {"A": "1/100", "B": "19/100", "C": "20/100", "D": "21/100", "E": "80/100"},
    "60291": {"A": "1/96",  "B": "1/64",   "C": "5/24",   "D": "1/4",    "E": "5/12"},
    "86572": {"A": "1",     "B": "4/7",    "C": "10/27",  "D": "14/81",  "E": "4/81"},
}
# Single options whose SECOND line was lost. In each the option is a stacked
# fraction at the very end of the item, where the denominator sits on its own
# line and the item boundary cut it. Each was read off the printed page:
#   2013 MT 51219 E  printed 145 AZUL day 2  "E 70 / 17"     -> 70/17
#   2013 MT 43849 E  printed 178 AZUL day 2  "E 28 / 5"      -> 28/5
#   2022 MT 86840 E  the AZUL fill shows "52" over "64", and the LEDOR booklet
#                    spells the same option "cinquenta e dois sessenta e
#                    quatro avos" -- two independent sources -> 52/64
# The corpus-wide check that found them: option E is NOT systematically
# truncated (its median length is 1.07-1.13x the median of A-D), so only the
# 11 items where E falls below half that median were inspected, and only these
# three were real.
PATCH_OPTION = {
    ("51219", "E"): "70/17",
    ("43849", "E"): "28/5",
    ("86840", "E"): "52/64",
}

NUMISH = re.compile(r"^[\d\s.,()−+\-×x*/^!_πa-zA-Z]{1,24}$")


def simple_fraction(v):
    v = (v or "").strip()
    if "\n" not in v or len(v) > 40:
        return None
    parts = [p.strip() for p in v.split("\n") if p.strip()]
    if len(parts) != 2:
        return None
    if not all(NUMISH.match(p) and any(c.isdigit() for c in p) for p in parts):
        return None
    return "/".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    n_dup = n_frac = n_tr = n_patch = 0
    for p in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        by = collections.defaultdict(list)
        for r in rows:
            by[r["item"]].append(r)
        touched = False
        for it, rs in by.items():
            # (C) transcription first -- it supersedes whatever is there
            if it in TRANSCRIBED:
                for r in rs:
                    want = TRANSCRIBED[it].get(r["resp_raw"])
                    if want and (r["option_text"] or "").strip() != want:
                        r["option_text"] = want
                        touched = True
                n_tr += 1
                continue
            for r in rs:
                want = PATCH_OPTION.get((it, r["resp_raw"]))
                if want and (r["option_text"] or "").strip() != want:
                    r["option_text"] = want
                    n_patch += 1
                    touched = True
            # (A) duplicate option text -> the whole set becomes NA
            real = [(r, (r["option_text"] or "").strip()) for r in rs]
            vals = [v for _, v in real if v and v != "NA"]
            if len(vals) >= 2 and len(vals) != len(set(vals)):
                for r, _ in real:
                    r["option_text"] = "NA"
                n_dup += 1
                touched = True
                continue
            # (B) stacked fraction -> inline
            for r, v in real:
                f = simple_fraction(v)
                if f:
                    r["option_text"] = f
                    n_frac += 1
                    touched = True
        if touched and a.apply:
            with open(p, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA); w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in SCHEMA})
    verb = "applied" if a.apply else "would apply"
    print(f"  {verb}: {n_dup} duplicate-option item(s) -> NA, "
          f"{n_frac} fraction option(s) inlined, {n_tr} item(s) transcribed, "
          f"{n_patch} truncated option(s) restored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
