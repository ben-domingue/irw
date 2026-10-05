#!/usr/bin/env python3
"""Re-interleave text the PDF's content stream emitted out of visual order.

WHY THIS EXISTS. Extraction follows the content stream, not the page. Where a
generator writes a row of glyphs in two passes -- all the digits, then all the
symbols between them -- the flattened text puts every symbol after every digit.
2019 MT 111518 is the case: its five options are chains of room numbers joined
by arrows, and they ship as

    A 14 54 16 14->->->-> ->-> ->

where the page reads `1 -> 4 -> 5 -> 4 -> 1 -> 6 -> 1 -> 4`. Nothing is wrong
with any character and nothing is missing, so every content gate stays green --
but the chain, which is the whole answer, is gone. The keyed option is affected.

WHAT MAKES THIS SAFE. The repair is a REORDER, never an addition, and that is
checked rather than asserted: the pass re-reads the printed line with
pymupdf's `sort=True` (which orders spans by position, not by stream order) and
substitutes ONLY if the character multiset of the old and new strings is
identical once whitespace is ignored. A candidate that fails that test is
reported and left alone -- the step-6 discipline of 53_stacked_fractions.py.
So this pass cannot invent, drop or alter a character; it can only move one.

SCOPE. Deliberately narrow. A row is a candidate only if its text contains two
arrows separated by nothing but whitespace, which is the signature of the
defect and not something ENEM prose produces. Measured over all 48 shipped
tables, `->\\s*->` matches 5 fields in exactly ONE item -- 2019 MT 111518's five
option rows -- and nothing else anywhere. For context `->` at all appears in 75
fields across 14 items, so the adjacency test is what does the work.

Usage:
  python3 56_reading_order.py --items-dir DIR --year YYYY --pdf P [--pdf P] [--apply]
"""
import argparse, collections, csv, glob, os, re, sys

import pymupdf

SCHEMA = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
          "item_text", "correct_response", "option_text", "resp", "item_text_translated",
          "option_text_translated", "instructions_translated", "section_prompt_translated",
          "language", "resp_raw"]
COLS = ("item_text", "option_text")

# The defect signature: two arrows with only whitespace between them.
ADJACENT = re.compile(r"→\s*→")


def bag(s):
    """Character multiset, whitespace ignored -- the reorder-only guard."""
    return collections.Counter(re.sub(r"\s+", "", s))


def sorted_lines(pdfs):
    """Every printed line of every page, read in VISUAL order."""
    out = []
    for p in pdfs:
        d = pymupdf.open(p)
        for i in range(d.page_count):
            txt = d[i].get_text("text", sort=True)
            for ln in txt.split("\n"):
                if ln.strip():
                    out.append((os.path.basename(p), i + 1, ln.strip()))
        d.close()
    return out


def candidates(items_dir):
    out = []
    for f in sorted(glob.glob(os.path.join(items_dir, "*__items.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            for c in COLS:
                v = r.get(c) or ""
                if ADJACENT.search(v):
                    out.append((f, r["item"], c, v))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--pdf", action="append", default=[])
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    cands = candidates(a.items_dir)
    if not cands:
        print("  no out-of-order candidates")
        return 0
    pdfs = [p for p in a.pdf if os.path.exists(p)]
    if not pdfs:
        print(f"  {len(cands)} candidate(s) but no readable --pdf; REPORTED, not rewritten")
        for f, it, c, v in cands:
            print(f"     {os.path.basename(f)} {it} [{c}]: {v[:60]!r}")
        return 0
    lines = sorted_lines(pdfs)

    # index the visual lines by their whitespace-free multiset
    by_bag = collections.defaultdict(list)
    for src, pg, ln in lines:
        by_bag[frozenset(bag(ln).items())].append((src, pg, ln))

    fixed = collections.Counter()
    reported = []
    for f in sorted({c[0] for c in cands}):
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        touched = False
        for r in rows:
            for c in COLS:
                v = r.get(c) or ""
                if not ADJACENT.search(v):
                    continue
                # The multiset alone is NOT an identifier. 2019 MT 111518's
                # options C, D and E are permutations of each other, so they
                # share a multiset: matching on it finds three candidates and
                # picking any of them gives three identical options. The option
                # LETTER is the discriminator -- 46_strip_option_letter.py
                # removes it from the cell, but the printed line still carries
                # it, and resp_raw says which one this row is.
                letter = (r.get("resp_raw") or "").strip() if c == "option_text" else ""
                if letter:
                    hits = []
                    for src, pg, ln in lines:
                        m = re.match(r"^" + re.escape(letter) + r"[\t ]+(.*)$", ln)
                        if m and bag(m.group(1)) == bag(v):
                            hits.append((src, pg, m.group(1)))
                else:
                    hits = by_bag.get(frozenset(bag(v).items()), [])
                # The same item is printed in BOTH the accessibility and the
                # standard booklet, so a correct match legitimately turns up
                # once per edition. That is not ambiguity: collapse hits whose
                # TEXT agrees and only refuse when the editions actually differ.
                uniq = sorted({h[2] for h in hits})
                if len(uniq) != 1:
                    reported.append((f, r["item"], c, v, len(uniq)))
                    continue
                hits = [next(h for h in hits if h[2] == uniq[0])]
                if len(hits) != 1:
                    reported.append((f, r["item"], c, v, len(hits)))
                    continue
                src, pg, ln = hits[0]
                if bag(ln) != bag(v):
                    reported.append((f, r["item"], c, v, -1))
                    continue
                if ADJACENT.search(ln):
                    reported.append((f, r["item"], c, v, -2))
                    continue
                r[c] = ln
                fixed[(r["item"], c)] += 1
                touched = True
        if touched and a.apply:
            with open(f, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA); w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in SCHEMA})

    print(f"  {'reordered' if a.apply else 'WOULD reorder'} {sum(fixed.values())} field(s) "
          f"over {len({k[0] for k in fixed})} item(s)")
    for (it, c), n in sorted(fixed.items()):
        print(f"     {it} [{c}] x{n}")
    for f, it, c, v, why in reported:
        tag = {-1: "multiset differs", -2: "visual line still has adjacent arrows"}.get(
            why, f"{why} visual line(s) matched, need exactly 1")
        print(f"     NOT rewritten: {it} [{c}] -- {tag}: {v[:52]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
