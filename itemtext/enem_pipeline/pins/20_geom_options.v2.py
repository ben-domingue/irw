#!/usr/bin/env python3
"""Recover option blocks the LINE-BASED parser cannot see, using coordinates.

WHY THIS EXISTS, and why it is a separate file.

12_parse_booklet_pdf works on pypdf's extracted *lines*, and finds an option
block by looking for five candidate lines whose letters read A-E. That is right
for almost every item. It has one structural blind spot, found in ENEM 2018 CN
printed position 126 (CO_ITEM 111411):

    'A'                     <- option A, alone on its line
    '15 20'
    'O OH D ClN+'           <- option D is IN HERE
    'B'
    'SO3'
    '  Na+'
    'E'
    ...
    'C'

The five options are bare chemical-structure figures set in two columns. Only
FOUR standalone letters survive line extraction -- A, B, E, C -- because `D`
sits on the same baseline as a figure's glyphs ('O' y=566.5, 'D' y=572.3,
'OH' y=574.1) and pypdf merges them into one line. So:

  * the ascending-subsequence rule reaches A,B,C and needs D  -> fails
  * the five-consecutive-candidates rule has only 4 candidates -> never runs
  * the R5 hollow-tail rule sees letters {A,B,C,E} != {A..E}   -> fails

This is a FOURTH failure mode, not one of the three the parser handles: not
"letters out of order", not "letters present but hollow", but a letter
ABSORBED INTO A FIGURE'S TEXT RUN. No rule that needs five letters in the line
stream can fire, and inventing the fifth would breach R5/R11.

The labels are, however, perfectly regular in coordinates:

    letter   x0      y       width
    A        60.4    572.3   9.7
    D       308.1    572.3   9.7
    B        60.4    630.4   9.7
    E       308.1    630.4   9.7
    C        60.4    711.2   9.7

Two x-positions, every label the same width, row-paired A|D, B|E, C. So this
module finds option labels as POSITIONED RUNS instead of as lines.

It does not edit the parser and does not replace it. It reads a booklet, emits
rows in 12_parse_booklet_pdf's own CSV schema for the positions you name, and
you merge them into that parser's output for 13_join.py. Use it only for
positions the parser reported as unparsed.

THE RULE, and the one trap in it
--------------------------------
An option label is a text run whose text is exactly one character A-E, sitting
at one of the LABEL X-POSITIONS. The label x-positions must be derived PER
ITEM, not per booklet: 2018 day 2 AZUL uses x=308.1 for a right-hand option
column in only two items out of ninety, so a booklet-wide "x used by >= 5
labels" filter drops it and the item stays broken. (I made exactly that mistake
first; it is why this is spelled out.)

Within an item we take the last set of five such runs whose letters are exactly
{A,B,C,D,E}, order them by the PRINTED LETTER (never by position -- two-column
layouts are out of reading order, EXTRACTION_RULES trap 2), and cut the stem at
the first label.

R5 is respected and not stretched: option_text is filled only from runs that
lie inside the option's own region. When the region holds no text other than
figure glyphs, the option ships as the literal NA. This module NEVER invents an
option label or an option text.

SCOPE -- MEASURED, AND NARROWER THAN IT LOOKS
---------------------------------------------
This is a TARGETED SUPPLEMENT, not a second parser. Use it only for positions
12_parse_booklet_pdf has reported as unparsed, and check its stem.

Measured on 18 positions of ENEM 2018 day 2 AZUL that the line parser handled
correctly: this module found five A-E labels on 13 of the 13 where it located
the marker at all, but it MISSED THE MARKER on 3 and found no label set on 2,
and its stem matched the parser's on only 1 of 13. The reason is `segment()`:
it assigns every run between two markers to the earlier one, in (y, x) reading
order, which scrambles item boundaries on ENEM's two-column pages. Fixing that
means reimplementing column detection, i.e. rewriting the parser, which is
explicitly not the intent here.

It is trustworthy where it is pointed at a single item whose region is
unambiguous. For 2018 CN 126 the result was verified two independent ways: the
five labels are at two x-positions with matching widths and row pairing, and
the recovered stem is character-identical (alphanumerics only, 9 lines) to
pypdf's own extraction of the same item.

Usage:
  python3 20_geom_options.py <booklet.pdf> --year 2018 --area CN \
      --position 126 [--position ...] --out geom.csv [--report]
"""
import argparse
import collections
import csv
import re
import sys

import pymupdf

LINE_TOL = 2.5   # points; runs within this of each other are one printed line
MARK = re.compile(r"^\s*QUEST[AÃ]O\s+(\d{1,3})\s*[.;:]?\s*$", re.I)
LETTERS = "ABCDE"
# page furniture that must never become option text
FURNITURE = re.compile(r"^\s*(\*[A-Z0-9]+\*|(LC|CH|CN|MT)\s*-\s*\d|P[áa]gina\s*\d+)")


def page_runs(page):
    """Positioned text runs: (y, x0, x1, text). One entry per span."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = s["text"].strip()
                if t:
                    out.append((round(s["bbox"][1], 1), round(s["bbox"][0], 1),
                                round(s["bbox"][2], 1), t))
    # Order by visual line, not by raw y. A bold/italic run on the same printed
    # line can sit a fraction of a point higher: in the 2018 CN 126 credit line
    # the journal name "Química Nova" (y=523.01, x=465.4) sits 0.9pt above the
    # sentence that contains it (y=523.92, x=184.8), so ordering on raw y puts
    # it before the author list. FIXED-WIDTH BUCKETING DOES NOT SOLVE THIS --
    # 523.01 and 523.92 straddle a 2.5pt bucket edge and still separate. So
    # cluster: walk y ascending and keep a run in the current line while it is
    # within LINE_TOL of the line's first run, then order each line by x.
    out.sort(key=lambda r: (r[0], r[1]))
    lines, cur = [], []
    for r in out:
        if cur and r[0] - cur[0][0] > LINE_TOL:
            lines.append(sorted(cur, key=lambda z: z[1])); cur = []
        cur.append(r)
    if cur:
        lines.append(sorted(cur, key=lambda z: z[1]))
    return [(y, x0, x1, t, i) for i, ln in enumerate(lines) for (y, x0, x1, t) in ln]


def booklet_runs(pdf):
    """All runs in reading order, tagged with their page."""
    doc = pymupdf.open(pdf)
    seq = []
    for pn in range(doc.page_count):
        for y, x0, x1, t, li in page_runs(doc[pn]):
            # global line id, so runs on one printed line can be rejoined with a
            # space instead of a newline
            seq.append((pn, y, x0, x1, t, (pn, li)))
    return seq


def segment(seq):
    """position -> the runs belonging to it, by walking the markers."""
    items, cur = collections.OrderedDict(), None
    for r in seq:
        m = MARK.match(r[4])
        if m:
            cur = int(m.group(1))
            items.setdefault(cur, [])
            continue
        if cur is not None:
            items[cur].append(r)
    return items


def find_options(runs):
    """Locate the five labels. Returns (label_runs_by_letter, stem_runs) or None.

    label_runs_by_letter maps 'A'..'E' -> the label run, so the caller can order
    by PRINTED letter rather than by position.
    """
    singles = [r for r in runs if len(r[4]) == 1 and r[4] in LETTERS]
    if len(singles) < 5:
        return None
    # Label x-positions, derived PER ITEM: an x used by at least two single
    # letters here. Two columns give two such x; one column gives one.
    # A real option column never repeats a LETTER. 2013 CN 72 sets its five
    # labels in BundesbahnPiStd-1 at x=37.1 (A,B,C) and x=296.8 (D,E), but the
    # circuit diagrams carry their own ammeter "A" labels, two of which happen
    # to share x=88.0. Counting positions alone admitted that as a third
    # column, and the five real labels were then no longer five CONSECUTIVE
    # candidates, so the A-E window never closed and the item was reported
    # unrecoverable. Requiring distinct letters per column drops the false
    # column without guessing which letters are real.
    by_x = collections.defaultdict(list)
    for r in singles:
        by_x[r[2]].append(r)
    cols = {x for x, rs in by_x.items()
            if len(rs) >= 2 and len({r[4] for r in rs}) == len(rs)}
    cand = [r for r in singles if r[2] in cols] or singles
    # last set of five covering A-E, scanning latest-first
    for st in range(len(cand) - 5, -1, -1):
        five = cand[st:st + 5]
        if {r[4] for r in five} == set(LETTERS):
            by = {r[4]: r for r in five}
            first = min((r[0], r[1]) for r in five)
            stem = [r for r in runs if (r[0], r[1]) < first]
            return by, stem
    return None


def option_bodies(runs, by):
    """Text lying in each option's own region, in reading order.

    An option's region runs from its label to the next label in READING order
    (page, y, x), which is how the page is actually laid out -- not to the next
    letter alphabetically.
    """
    pos = sorted(((by[L][0], by[L][1], L) for L in LETTERS))
    bounds = {}
    for i, (y, x, L) in enumerate(pos):
        nxt = (pos[i + 1][0], pos[i + 1][1]) if i + 1 < len(pos) else (float("inf"),) * 2
        bounds[L] = ((y, x), nxt)
    out = {}
    for L in LETTERS:
        (lo, hi) = bounds[L]
        out[L] = runs_to_text([r for r in runs
                               if lo < (r[0], r[1]) < hi and not FURNITURE.match(r[4])])
    return out


PROSE = re.compile(r"[^\W\d_]{3,}", re.UNICODE)


def runs_to_text(runs):
    """Rejoin runs into printed lines: space within a line, newline between.

    Without this the credit line of 2018 CN 126 comes out as three separate
    lines, because its author list, its italic journal name and its issue
    number are three spans of one printed line.
    """
    out, cur, cur_id = [], [], None
    for r in runs:
        if cur and r[5] != cur_id:
            out.append(" ".join(cur)); cur = []
        cur.append(r[4]); cur_id = r[5]
    if cur:
        out.append(" ".join(cur))
    txt = "\n".join(out).strip()
    # Joining spans with a space puts one before punctuation when the preceding
    # span is styled: "Química Nova , n. 5" for the printed "Química Nova, n. 5".
    return re.sub(r"\s+([,.;:?!])", r"\1", txt)


def trim_stem(stem_runs):
    """Drop trailing non-prose runs from the stem.

    An option figure's glyphs can sit ABOVE the first option label: in 2018 CN
    126 the structures start at y=566.5 ('O'), 568.6 ('Cl'), 571.0 ('N+') while
    the first label is at y=572.3, so cutting the stem at the first label alone
    leaves 'O\nCl\nN\n+' hanging off the end of the stem. Those glyphs belong
    to the option figures, which R5 ships as NA, so they are dropped -- but only
    from the TAIL, and only while the run carries no 3+-letter word. Every ENEM
    stem ends in a prose lead-in ('... mencionado no texto?'), so this cannot
    eat real stem text; 'Cl', 'O', 'N', '+', '15', '20' are not prose and go.
    """
    out = list(stem_runs)
    while out and not PROSE.search(out[-1][4]):
        out.pop()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--year", required=True)
    ap.add_argument("--area", required=True)
    ap.add_argument("--position", action="append", type=int, required=True)
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--figure-options", action="store_true",
                    help="options are bare figures: ship the literal NA (R5). "
                         "Without this the extracted body text is kept.")
    a = ap.parse_args()

    items = segment(booklet_runs(a.pdf))
    rows, missing = [], []
    import os
    src = os.path.basename(a.pdf)
    for pos in a.position:
        runs = items.get(pos)
        if not runs:
            missing.append((pos, "no marker found")); continue
        got = find_options(runs)
        if not got:
            missing.append((pos, "no five A-E labels at any label x-position")); continue
        by, stem = got
        bodies = option_bodies(runs, by)
        stem = trim_stem([r for r in stem if not FURNITURE.match(r[4])])
        stem_txt = runs_to_text(stem)
        if a.report:
            print(f"  position {pos}: five labels found")
            for L in LETTERS:
                r = by[L]
                print(f"     {L}  p{r[0] if False else ''} y={r[1]:7.1f} x={r[2]:6.1f} "
                      f"w={r[3]-r[2]:.1f}  body={bodies[L][:46]!r}")
            print(f"     stem ends: ...{stem_txt[-70:]!r}")
        for L in LETTERS:
            txt = "NA" if a.figure_options else (bodies[L] or "NA")
            rows.append({"year": a.year, "area": a.area, "lang_block": "",
                         "position": pos, "option_letter": L,
                         "stem": stem_txt, "option_text": txt,
                         "source_file": src})
    for pos, why in missing:
        print(f"  position {pos}: NOT recovered -- {why}", file=sys.stderr)
    if a.out and rows:
        with open(a.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["year", "area", "lang_block", "position",
                                               "option_letter", "stem", "option_text",
                                               "source_file"])
            w.writeheader()
            w.writerows(rows)
        print(f"  wrote {len(rows)} row(s) for {len(rows)//5} item(s) -> {a.out}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
