#!/usr/bin/env python3
"""Restore stacked fractions that PDF text extraction flattened.

WHY THIS EXISTS. A printed fraction is a numerator, a drawn rule, and a
denominator. Text extraction reads them in layout order and emits them as two
ordinary tokens, so `7/5` becomes `7 5` and `OR = (1/4) OM` becomes
`OR = 1 4 OM`. No character is wrong, nothing is missing, and every content
gate stays green -- but the arithmetic is gone. A model answering
2013 MT 43849 from `AC = 7 BD5` cannot get it right, and in the 100-item
model-understanding check it did not.

The size-based superscript detector in 48_mark_scripts.py cannot see these:
a stacked numerator is printed at FULL body size, just on a raised baseline.
The only reliable signal is the fraction bar itself, which is a drawing, not
text.

THE RULE (deliberately narrow -- a missed fraction is better than an invented
one):

  1. Find candidate bars: a drawn rect no taller than 1.8pt, 3-70pt wide,
     clear of the header and footer bands.
  2. Drop table rules: any two bars sharing a baseline on the same page.
  3. Require text tightly above AND below, each no wider than 1.25x the bar
     and centred on it within 30% of its width. Word bboxes carry the font's
     ascender and descender, so the numerator's box dips BELOW the bar and the
     denominator's rises ABOVE it; the y-tolerances allow for that.
  4. Confirm the flattened form `<num> <den>` -- exactly one space, both sides
     at token boundaries -- actually occurs in that page's reading order.
  5. Locate the shipped row by an exact context substring taken around the
     occurrence, so the rewrite is anchored to the item it was measured in.
  6. Rewrite to `<num>/<den>` ONLY where the flattened form occurs exactly as
     often in the row as the page has bars for that pair. Any mismatch is
     reported and left alone.

Step 6 is what keeps `ABO` from becoming `AB/O` and an axis label reading
`anos x` from becoming `s/x`: those never survive the token-boundary and
count tests.

Usage:
  python3 53_stacked_fractions.py --tables DIR [--year YYYY] [--apply]
Without --apply it only reports.
"""
import argparse, collections, csv, glob, os, re, sys, unicodedata
from _rawedit import rewrite_field
import pymupdf

ENEM = os.path.expanduser("~/enem")
SCRATCH = "/scratch/users/mazzafe/itemtext_years"

def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s or "")).strip()

# What either side of a fraction can look like: a number (possibly with the
# thin-space thousands grouping INEP uses, "1 000"), or a short algebraic
# token. Anything wordier is prose that happens to sit over a rule -- the
# second, independent guard against 2023 CN 66330's "Teste/1".
SIDE = re.compile(r"[0-9]{1,4}(?: [0-9]{3})*(?:[.,][0-9]{1,3})?"
                  r"|[A-Za-z\u0391-\u03c9\u2113][A-Za-z0-9\u2080-\u2089]{0,2}")


def bars_on(pg):
    H = pg.rect.height
    out = [dr["rect"] for dr in pg.get_drawings()
           if dr["rect"].height <= 1.8 and 3 <= dr["rect"].width <= 70
           and dr["rect"].y0 >= 55 and dr["rect"].y1 <= H - 70]
    # the same rule is sometimes stroked twice; that is one bar, not two
    uniq, keys = [], set()
    for r in out:
        k = (round(r.x0), round(r.y0), round(r.x1))
        if k not in keys:
            keys.add(k); uniq.append(r)
    # A table shows up two ways and BOTH have to be excluded. Cells side by
    # side share a baseline. Cells stacked in one column share an x-range --
    # 2023 CN 66330 is a column of five borders at x=35.9-100.8, 14.7pt apart,
    # which reads as the fractions Teste/1, 1/2, 2/3, 3/4, 4/5.
    ys = collections.Counter(round(r.y0) for r in uniq)
    xs = collections.Counter((round(r.x0), round(r.x1)) for r in uniq)
    return [r for r in uniq
            if ys[round(r.y0)] < 2 and xs[(round(r.x0), round(r.x1))] < 2]


def fracs(pg):
    words = pg.get_text("words"); res = []
    for r in bars_on(pg):
        cx, w_ = (r.x0 + r.x1) / 2, r.width
        up = [w for w in words if -4 < r.y0 - w[3] < 4 and w[0] < r.x1 + 1 and w[2] > r.x0 - 1]
        dn = [w for w in words if -4 < w[1] - r.y1 < 6 and w[0] < r.x1 + 1 and w[2] > r.x0 - 1]
        if not (up and dn):
            continue
        def centred(g):
            x0 = min(x[0] for x in g); x1 = max(x[2] for x in g)
            return (x1 - x0) <= w_ * 1.25 and abs((x0 + x1) / 2 - cx) <= w_ * 0.30
        if not (centred(up) and centred(dn)):
            continue
        u = "".join(w[4] for w in sorted(up, key=lambda w: w[0])).strip()
        v = "".join(w[4] for w in sorted(dn, key=lambda w: w[0])).strip()
        if not (SIDE.fullmatch(u) and SIDE.fullmatch(v)):
            continue
        res.append((u, v))
    return res


def pat(u, v, raw=False):
    """`u` then `v`, with a token boundary on each outer edge.

    Two variants, and using the wrong one is silent: the PAGE text is
    normalised to single spaces, but the STORED stem keeps the line break the
    fraction was printed across ('54\\n100'). Matching stored text with the
    single-space pattern finds nothing while every count reads zero.
    """
    gap = r"(?:[ \t]*\n[ \t]*|[ \t]+)" if raw else " "
    lb = r"(?<![0-9A-Za-z\u00c0-\u017f])" if re.match(r"[0-9A-Za-z\u00c0-\u017f]", u) else ""
    rb = r"(?![0-9A-Za-z\u00c0-\u017f])" if re.search(r"[0-9A-Za-z\u00c0-\u017f]$", v) else ""
    return lb + re.escape(u) + gap + re.escape(v) + rb


def booklets(year):
    """The PDFs the pipeline itself reads.

    Font-repaired years (2015, 2016, 2018, 2021) MUST come from rb_repaired:
    their INEP originals carry broken encodings, so the extracted-text side of
    the confirmation step would never match the shipped rows. Drawings are
    untouched by the repair, so the bars are the same either way.

    Every colour variant is scanned. They carry the same items in a different
    order, and the confirmation step is anchored to text, so a booklet that
    contributed nothing simply produces no hits.
    """
    rep = sorted(glob.glob(f"{SCRATCH}/{year}/rb_repaired/*.pdf"))
    out = list(rep)
    for p in sorted(glob.glob(f"{ENEM}/extracted_{year}/**/*.pdf", recursive=True)):
        b = os.path.basename(p)
        if re.search(r"GAB|LIBRAS|LEIA|Edital|Matriz|Cartilha|Guia|Manual|Procedimentos|reda",
                     b, re.I):
            continue
        out.append(p)
    return out


# Fractions the automatic rule will not touch, verified by eye against the
# printed page. Two reasons it declines, both deliberate:
#   * side-by-side fractions on one printed line share a baseline, so step 2
#     drops them as a table rule and the bar count comes up short;
#   * reading order can separate a numerator from its denominator entirely, so
#     the flattened pair never appears adjacent for step 4 to find.
# Each entry cites the page it was read off. Anything not verifiable that way
# does not belong here.
PATCH_STEM = [
    # Caderno7_Azul_Dom p28. Every "n over 100" in this item is a fraction:
    # the quality table reads 0 <= P < 2/100 Excelente, 2/100 <= P < 4/100 Bom,
    # and so on. The bars are side by side on each table line, so step 2 drops
    # them. 54/100 in the opening sentence stands alone and is done
    # automatically.
    ("2013", "42907", "25\n1 000\n eram", "25/1 000 eram"),
    ("2013", "42907", "38\n1 000  dos", "38/1 000 dos"),
    ("2013", "42907", "0 \u2264 P < 2\n100 Excelente", "0 \u2264 P < 2/100 Excelente"),
    ("2013", "42907", "2\n100 \u2264 P < 4\n100 Bom", "2/100 \u2264 P < 4/100 Bom"),
    ("2013", "42907", "4\n100 \u2264 P < 6\n100 Regular", "4/100 \u2264 P < 6/100 Regular"),
    ("2013", "42907", "6\n100 \u2264 P < 8\n100 Ruim", "6/100 \u2264 P < 8/100 Ruim"),
    ("2013", "42907", "8\n100 \u2264 P \u2264 1 P\u00e9ssimo", "8/100 \u2264 P \u2264 1 P\u00e9ssimo"),

    # Caderno7_Azul_Dom p31. Printed: "Considere que AC = 7/5 BD", with AC and
    # BD carrying segment overlines and the 7 stacked over the 5 at x=134.
    # Reading order emits the 5 after BD, giving "AC = 7 BD5", so the pair is
    # never adjacent and step 4 cannot see it. This is the item the 100-item
    # model check got wrong, and this is why. The l/BD later in the same stem
    # IS adjacent and is done automatically.
    ("2013", "43849", "AC = 7 BD5   e que", "AC = 7/5 BD e que"),
    # Same page, same item. "razao l/BD" carries TWO rules 3pt apart: the
    # fraction bar at y=347.14 (x 202.10-220.08) and the SEGMENT OVERLINE on
    # BD at y=349.99 (x 203.50-219.09, matching the glyphs exactly). Both sit
    # between the same numerator and denominator words, so step 6 counts two
    # bars against one flattened pair and declines. It is right to: the two
    # are not distinguishable by geometry alone at this tolerance.
    ("2013", "43849", "raz\u00e3o l\nBD\n para", "raz\u00e3o l/BD para"),
]


def apply_patches(tables, apply_, items_dir=None, only_year=None):
    done = 0
    for year, item, old, new in PATCH_STEM:
        if items_dir and year != only_year:
            continue
        hit = False
        for f in (sorted(glob.glob(f"{items_dir}/*__items.csv")) if items_dir
                  else sorted(glob.glob(f"{tables}/batch_enem_{year}/*__items.csv"))):
            rows = list(csv.DictReader(open(f)))
            if not any(r["item"] == item and old in (r["item_text"] or "") for r in rows):
                continue
            hit = True
            if apply_:
                tgt = [r for r in rows if r["item"] == item]
                before = tgt[0]["item_text"]
                rewrite_field(f, before, before.replace(old, new), expect=len(tgt))
            done += 1
            print(f"  {year} {item:>7}  PATCH {'applied' if apply_ else 'pending'}: "
                  f"{old[:34]!r} -> {new[:34]!r}")
        if not hit:
            print(f"  {year} {item:>7}  PATCH ALREADY APPLIED OR TEXT CHANGED: {old[:44]!r}")
    return done


def year_files(tables, items_dir, year, years):
    """Either layout: the batch tree, or one year's out dir inside 42_rebuild."""
    if items_dir:
        return [(year, sorted(glob.glob(f"{items_dir}/*__items.csv")))]
    return [(y, sorted(glob.glob(f"{tables}/batch_enem_{y}/*__items.csv"))) for y in years]


def run(tables, years, apply_, items_dir=None, only_year=None):
    report, rewritten = [], 0
    for year, files in year_files(tables, items_dir, only_year, years):
        if not files:
            continue
        rows = {f: list(csv.DictReader(open(f))) for f in files}
        # Normalise every stem ONCE. Doing it inside the page loop costs a
        # full pass over ~900 rows per bar per page per booklet, which turns a
        # two-minute step into a forty-minute one and makes the whole pass too
        # slow to keep in 42_rebuild.py.
        nstem = {f: [norm(r.get("item_text")) for r in rs] for f, rs in rows.items()}
        want = collections.defaultdict(collections.Counter)   # (file,rowidx) -> Counter[(u,v)]
        for p in booklets(year):
            try:
                d = pymupdf.open(p)
            except Exception:
                continue
            for i in range(d.page_count):
                ptext = norm(d[i].get_text())
                page_bars = collections.Counter(fracs(d[i]))
                for (u, v), nbar in page_bars.items():
                    m = re.search(pat(u, v), ptext)
                    if not m:
                        continue
                    ctx = ptext[max(0, m.start() - 30): m.end() + 8]
                    if len(ctx) < 22:
                        continue
                    for f, rs in rows.items():
                        hit = next((j for j, st in enumerate(nstem[f]) if ctx in st), None)
                        if hit is None:
                            continue
                        want[(f, rs[hit]["item"])][(u, v)] = max(
                            want[(f, rs[hit]["item"])][(u, v)], nbar)
                        break
        for (f, item), pairs in sorted(want.items()):
            for (u, v), nbar in sorted(pairs.items()):
                targets = [r for r in rows[f] if r["item"] == item]
                if not targets:
                    continue
                n = len(re.findall(pat(u, v, raw=True), targets[0].get("item_text") or ""))
                if n == 0:
                    continue
                if n != nbar:
                    # side-by-side fractions on one line share a baseline, so
                    # step 2 drops them as a table rule and the counts diverge.
                    # Report; a human decides. PATCH_STEM carries the verdicts.
                    covered = any(y == year and i == item for y, i, _o, _n in PATCH_STEM)
                    report.append((year, item, u, v,
                                   f"AMBIGUOUS {n} in text vs {nbar} bars -- "
                                   + ("resolved by PATCH_STEM" if covered else "left alone")))
                    continue
                if apply_:
                    old = targets[0]["item_text"] or ""
                    newv = re.sub(pat(u, v, raw=True), f"{u}/{v}", old)
                    rewrite_field(f, old, newv, expect=len(targets))
                    for r in targets:
                        r["item_text"] = newv
                rewritten += 1
                report.append((year, item, u, v,
                               f"{'rewrote' if apply_ else 'would rewrite'} {len(targets)} rows"))
    apply_patches(tables, apply_, items_dir, only_year)
    for y, it, u, v, what in report:
        print(f"  {y} {it:>7}  {u}/{v:<8} {what}")
    print(f"\n{rewritten} row-level rewrites across {len({(r[0], r[1]) for r in report})} items")
    return rewritten

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables")
    ap.add_argument("--items-dir", help="one year's out dir, as used by 42_rebuild.py")
    ap.add_argument("--year", action="append")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.items_dir and not (a.year and len(a.year) == 1):
        ap.error("--items-dir needs exactly one --year")
    if not (a.items_dir or a.tables):
        ap.error("give --tables or --items-dir")
    ys = a.year or [d.split("_")[-1] for d in sorted(glob.glob(f"{a.tables}/batch_enem_*"))]
    sys.exit(0 if run(a.tables, ys, a.apply,
                      items_dir=a.items_dir,
                      only_year=(a.year[0] if a.year else None)) >= 0 else 1)
