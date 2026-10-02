#!/usr/bin/env python3
"""Recover glyphs the booklet DRAWS instead of setting as text.

WHY THIS EXISTS. A radical and an equilibrium arrow are not characters in these
booklets -- they are vector artwork. The text layer has a HOLE where they are
printed, so extraction yields a stem that reads

    Utilize 1,7 como aproximacao para 3.             (2013 MT 16538)
    Cl_2 (g) + 2 H_2O (l)  HClO (aq) + H_3O^+ (aq)   (2013 CN 29002)

for a page that prints a square root and an equilibrium arrow. From the
extractor's point of view no character is wrong and none is missing, so every
content gate stays green while the mathematics and the chemistry are gone.

THE PRECEDENT AND THE RULING. 53_stacked_fractions.py already reads geometry
rather than text for exactly this reason -- R12: "The only reliable signal is
the fraction bar itself, which is a drawing, not text." Mateus ruled on
2026-10-02 that recovering a glyph the same way is likewise RECOVERY, not
generation: "we are not really generating, we are only looking and recovering
in a feasible manner." R16 in EXTRACTION_RULES.md states it.

IT IS AN EQUILIBRIUM ARROW, NOT A ONE-WAY ARROW. The review that surfaced these
described them as "reaction arrow lost", and writing a one-way arrow would have
shipped a one-way reaction where INEP printed an equilibrium -- inverting the
chemistry of three items. The geometry settles it: each arrow is two
ANTIPARALLEL harpoons, a shaft left-to-right with its head at the right end and
a second right-to-left with its head at the left. All three stems corroborate
it independently -- 29002 gives pK_a, 13038 gives K 1 / K 2 / K_3, 83631 says
"em equilibrio no sangue" -- and the character already ships in the corpus
(2016 CN 40112), as do the radical (four items) and the script ell. None of
this is new notation.

=============================================================================
GEOMETRY FINDS AND VERIFIES; AN EXPLICIT TABLE APPLIES
=============================================================================
Two halves, deliberately separated, because they fail in different ways.

THE AUDIT is geometric and reproducible, and it is what lets this pass run
usefully on a new year. A drawing is a candidate only if it sits INSIDE AN
INTRA-LINE TEXT GAP: spans grouped by baseline y-centre, sorted by x, a gap
being >= 4pt of clear space between consecutive spans. That condition does
nearly all the work -- measured over the 30 booklets the pipeline reads:

    radical hook signature        15 raw  ->  3 inside a gap
    equilibrium, one drawing       6 raw  ->  5 inside a gap
    equilibrium, paired halves     2 raw  ->  2 inside a gap

...but THE GAP ALONE IS NOT ENOUGH, and a sweep that stops there reports no
false positives only because it has not looked. Two structural requirements
remove the two survivors:

  * A RADICAL HOOK NEEDS ITS VINCULUM. The hook is a filled path of 8 segments;
    the bar over the radicand is a SEPARATE zero-height stroked line abutting
    its top right. Requiring it drops 2017 std_d2 p6, where the hook signature
    appears between two "Eletricidade" labels in a diagram. 3 -> 2.
  * AN EQUILIBRIUM HALF NEEDS ITS ANTIPARALLEL PARTNER. 2013's generator
    strokes the two harpoons as two 2-segment drawings; 2015's strokes both in
    one 4-segment drawing. A LONE half is not an equilibrium arrow. Requiring
    the pair -- x-aligned within 1.5pt, 3-7pt apart vertically, heads at
    OPPOSITE ends -- drops 2022 std_d2 p2, where a figure element sits between
    "SOLO" and a question header. Opposite heads also separate an equilibrium
    from two parallel arrows, which would mean something else entirely.

With both in place the audit yields 9 glyphs in 5 items and nothing else in the
corpus. ZERO-HEIGHT PATHS ARE REAL: the vinculum has rect.height == 0.0, so the
usual "height > 0.5" filter silently discards it.

THE TABLE applies, and the audit REFUSES to run when it finds more glyphs than
the table accounts for -- the same contract as 54_relocate_descriptions.py.
Anchoring the geometry automatically to a shipped cell was tried and abandoned;
each reason is a trap worth recording:

  * the spans adjoining a gap are often a fragment -- "O (l) " or "+" -- that
    recurs across many items. A dry run on that basis offered to write a
    radical into 2013 MT 51250 and 51395, and an equilibrium arrow into 2015 CN
    25964 and 83854, none of them the item the glyph was measured in;
  * widening the anchor to the whole printed line needs pymupdf's own line
    grouping, which SPLITS a line at a wide gap -- precisely where the glyph
    sits -- so the arrows stop being intra-line gaps and vanish;
  * grouping by y-centre instead keeps the gaps but scatters every sub- and
    superscript onto a row of its own, so the line reads "Cl (g) + 2 HO (l)"
    and cannot match a shipped "Cl_2 (g) + 2 H_2O (l)";
  * and 2015 p25's anchors come out as "D++" and "+2--11" either way.

Eleven entries, each read off the page, is smaller and auditable. It is what
55_recover_tables.py does, for the same reason.

Usage:
  python3 57_drawn_glyphs.py --items-dir DIR --year YYYY --pdf P [--pdf P] [--apply]
"""
import argparse, collections, csv, glob, os, sys

import pymupdf

SCHEMA = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
          "item_text", "correct_response", "option_text", "resp", "item_text_translated",
          "option_text_translated", "instructions_translated", "section_prompt_translated",
          "language", "resp_raw"]

GAP_MIN = 4.0
EQ = "⇌"          # RIGHTWARDS HARPOON OVER LEFTWARDS HARPOON
SQ = "√"          # SQUARE ROOT
DL = "Δ"          # GREEK CAPITAL DELTA
MN = "−"          # MINUS SIGN

# (year, item, column, option letter or None, verbatim old, verbatim new, evidence)
# Every `old` was read off the shipped cell; every `new` off the printed page.
# A double space inside an `old` is the hole the drawn glyph left behind.
GLYPHS = [
    # ---- 2013 CN 29002: two equilibria, each drawn as a PAIR of harpoons ----
    ("2013", "29002", "item_text", None,
     "H_2O (l)  HClO (aq)", "H_2O (l) " + EQ + " HClO (aq)",
     "Caderno1_Azul_Sab p21. Two 2-segment stroked paths at "
     "(386.5,152.1,399.3,155.4) and (386.9,157.3,399.6,160.6): the first runs "
     "left-to-right with its head at the RIGHT end, the second right-to-left "
     "with its head at the LEFT -- antiparallel, i.e. an equilibrium. The stem "
     "gives pK_a = -log K_a = 7,53."),
    ("2013", "29002", "item_text", None,
     "H_2O (l)  H3O+ (aq)", "H_2O (l) " + EQ + " H3O+ (aq)",
     "Caderno1_Azul_Sab p21, second equation. Paired paths at "
     "(367.9,178.2,380.6,181.5) and (368.2,183.4,380.9,186.8), same shape."),
    # ---- 2013 MT: two radicals, hook + vinculum ----
    ("2013", "16538", "item_text", None,
     "aproximação para 3.", "aproximação para " + SQ + "3.",
     "Caderno7_Azul_Dom p20. Filled 8-segment hook at "
     "(192.5,520.9,197.6,530.4) with its vinculum, a zero-height stroked line "
     "at (197.6,521.1,205.0,521.1) spanning exactly the '3'. 2015 MT 81583 "
     "ships the identical sentence already correct, so the form is settled."),
    ("2013", "13512", "option_text", "E",
     "2 6 m", "2" + SQ + "6 m",
     "Caderno7_Azul_Dom p31, option E. Hook at (316.3,153.0,321.3,162.5); "
     "vinculum at (321.3,153.1,329.1,153.1) covers only the '6', so the "
     "radicand is 6 and the leading 2 is a coefficient."),
    # ---- 2015 CN 13038: four equilibria, each ONE 4-segment drawing ----
    ("2015", "13038", "item_text", None,
     "H_2O (l)  Ca2+ (aq)", "H_2O (l) " + EQ + " Ca2+ (aq)",
     "std_d1 p25, equation (I). One stroked path of 4 segments at "
     "(427.5,202.1,444.8,207.9), two antiparallel shafts with heads at "
     "opposite ends. The item's K 1 = 3,0x10-11, K 2 = 6,0x10-9 and "
     "K_3 = 2,5x10^-7 are equilibrium constants."),
    ("2015", "13038", "item_text", None,
     "− (aq)  H+ (aq) + CO_3", "− (aq) " + EQ + " H+ (aq) + CO_3",
     "std_d1 p25, equation (II). Path at (360.4,222.3,377.8,228.1)."),
    ("2015", "13038", "item_text", None,
     "CaCO_3 (s)  Ca2+ (aq)", "CaCO_3 (s) " + EQ + " Ca2+ (aq)",
     "std_d1 p25, equation (III). Path at (358.3,242.4,375.7,248.3)."),
    ("2015", "13038", "item_text", None,
     "H_2O (l)  H+ (aq) + HCO_3", "H_2O (l) " + EQ + " H+ (aq) + HCO_3",
     "std_d1 p25, equation (IV). Path at (379.2,261.6,396.5,267.4)."),
    ("2015", "83631", "item_text", None,
     "O_2 (aq)  HbO_2 (", "O_2 (aq) " + EQ + " HbO_2 (",
     "std_d1 p16. Path at (176.8,261.1,194.2,266.9), 4 segments, "
     "antiparallel. The stem says the haemoglobin is 'em equilibrio no "
     "sangue, conforme a relacao'."),
    # ---- 2015 CN 25964: Delta and minus, both drawn as SUB-PATHS ----
    #
    # The one case the audit cannot find, and the reason the table exists at
    # all. Both Deltas are sub-paths of ONE stroked drawing at
    # (131.9,258.1,197.6,327.4) and both minus signs of another at
    # (166.9,261.8,229.8,323.6), so no per-drawing filter can isolate them --
    # a sweep for standalone 3-segment triangles over the six standard
    # booklets returns 0. They also sit INSIDE A FIGURE rather than an
    # intra-line gap, so the audit's discriminating condition is unavailable.
    #
    # SCOPE NOTE: this item's subscripts are additionally collected at the end
    # of the cell as a bare digit run ("kJ/g\n2\n2\n2\n2\n2\n1\n2"), a
    # reading-order defect of the same family as 2019 MT 111518. That is not
    # what the review flagged here and is left alone; only the missing Delta
    # and minus are restored.
    ("2015", "25964", "item_text", None,
     "H  =   18,8 kJ/g", DL + "H  =   " + MN + "18,8 kJ/g",
     "std_d1 p29. rawdict per character proves the text layer holds three real "
     "U+0020 where the minus belongs and nothing where the Delta belongs. The "
     "Delta is a 3-segment sub-path (131.9,265.4)-(138.7,265.4)-(135.3,258.1), "
     "immediately left of the label span's x0=139.0; the minus is a sub-path "
     "(166.9,261.8)-(171.6,261.8). Enthalpy of combustion is negative."),
    ("2015", "25964", "item_text", None,
     "H  =   2,4 kJ/g", DL + "H  =   " + MN + "2,4 kJ/g",
     "std_d1 p29, second label. Delta sub-path at (190.8..197.6, "
     "320.0..327.4), span x0=197.9; minus sub-path "
     "(225.1,323.6)-(229.8,323.6)."),
]


def nl(dr):
    return sum(1 for it in dr["items"] if it[0] == "l")


def head_side(dr):
    """'r' if the arrowhead sits at the right end of the shaft, else 'l'."""
    ls = [it for it in dr["items"] if it[0] == "l"]
    if len(ls) < 2:
        return None
    shaft = max(ls, key=lambda it: abs(it[2].x - it[1].x))
    bx0, bx1 = sorted((shaft[1].x, shaft[2].x))
    rest = [it for it in ls if it is not shaft]
    if not rest:
        return None
    hx = sum(c for it in rest for c in (it[1].x, it[2].x)) / (2.0 * len(rest))
    return "r" if abs(hx - bx1) < abs(hx - bx0) else "l"


def gaps_on(pg):
    """[(x0, x1, ytop, ybot, left_span_text, right_span_text)] per intra-line gap.

    Grouped by baseline y-centre, NOT by pymupdf's line grouping: that splits a
    line at a wide gap, which is exactly where a drawn glyph sits.
    """
    rows = collections.defaultdict(list)
    for b in pg.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                if sp["text"].strip():
                    rows[round((sp["bbox"][1] + sp["bbox"][3]) / 2.0, 0)].append(sp)
    out = []
    for _, sps in rows.items():
        sps.sort(key=lambda s: s["bbox"][0])
        for a, b2 in zip(sps, sps[1:]):
            if b2["bbox"][0] - a["bbox"][2] >= GAP_MIN:
                out.append((a["bbox"][2], b2["bbox"][0],
                            min(a["bbox"][1], b2["bbox"][1]),
                            max(a["bbox"][3], b2["bbox"][3]),
                            a["text"], b2["text"]))
    return out


def in_gap(r, gl):
    hit = [g for g in gl
           if g[0] - 1.5 <= r.x0 and r.x1 <= g[1] + 1.5
           and g[2] - 7 <= r.y0 and r.y1 <= g[3] + 7]
    return hit[0] if hit else None


def audit(pdfs):
    """[(glyph, src, page, left_text, right_text)] for every drawn glyph found."""
    out = []
    for p in pdfs:
        d = pymupdf.open(p)
        for i in range(d.page_count):
            pg = d[i]
            drs = pg.get_drawings()
            gl = gaps_on(pg)
            if not gl:
                continue
            vinc = [dr for dr in drs if dr["type"] == "s" and nl(dr) == 1
                    and abs(dr["rect"].y1 - dr["rect"].y0) < 0.6]
            for dr in drs:
                r = dr["rect"]; w = r.x1 - r.x0; h = r.y1 - r.y0
                if dr["type"] == "f" and nl(dr) == 8 and 4.0 < w < 7.0 and 8.5 < h < 11.0:
                    g = in_gap(r, gl)
                    if g and any(abs(q["rect"].x0 - r.x1) < 2.0
                                 and abs(q["rect"].y0 - r.y0) < 2.0 for q in vinc):
                        out.append((SQ, os.path.basename(p), i + 1, g[4], g[5]))
                elif dr["type"] == "s" and nl(dr) == 4 and 15 < w < 22 and 4 < h < 8:
                    g = in_gap(r, gl)
                    if g:
                        out.append((EQ, os.path.basename(p), i + 1, g[4], g[5]))
            halves = [dr for dr in drs if dr["type"] == "s" and nl(dr) == 2
                      and 10 < (dr["rect"].x1 - dr["rect"].x0) < 16
                      and 2 < (dr["rect"].y1 - dr["rect"].y0) < 5]
            used = set()
            for a_ in halves:
                if id(a_) in used:
                    continue
                for b_ in halves:
                    if b_ is a_ or id(b_) in used:
                        continue
                    ra, rb = a_["rect"], b_["rect"]
                    if abs(ra.x0 - rb.x0) > 1.5 or abs(ra.x1 - rb.x1) > 1.5:
                        continue
                    if not (3.0 <= abs(ra.y0 - rb.y0) <= 7.0):
                        continue
                    hs = head_side(a_)
                    if hs is None or hs == head_side(b_):
                        continue
                    g = in_gap(ra, gl) or in_gap(rb, gl)
                    if g:
                        out.append((EQ, os.path.basename(p), i + 1, g[4], g[5]))
                    used.add(id(a_)); used.add(id(b_))
                    break
        d.close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--pdf", action="append", default=[])
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    mine = [g for g in GLYPHS if g[0] == a.year]
    pdfs = [p for p in a.pdf if os.path.exists(p)]

    # THE AUDIT. The same printed glyph is reachable from both booklet
    # editions, so dedupe on (glyph, page, surrounding text) before counting.
    found = audit(pdfs) if pdfs else []
    uniq = {(ch, pg, lt.strip()[-24:], rt.strip()[:24]) for ch, src, pg, lt, rt in found}
    n_found = len(uniq)
    n_table = sum(1 for g in mine if EQ in g[5] or SQ in g[5])
    print("  audit: %d drawn glyph(s) in a text gap; table accounts for %d"
          % (n_found, n_table))
    if n_found > n_table:
        print("  REFUSING TO APPLY -- a page carries a drawn glyph this pass does "
              "not know about:")
        for k in sorted(uniq):
            print("     %r p%s  %r | %r" % k)
        print("\n  Verify each against the printed page and add it to GLYPHS, or "
              "record why it is not a glyph. Do not let this run unclassified.")
        return 1

    done = collections.Counter(); skipped = []
    for f in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        touched = False
        for _y, item, col, letter, oldv, newv, _why in mine:
            for r in rows:
                if r["item"] != item:
                    continue
                if letter is not None and (r.get("resp_raw") or "").strip() != letter:
                    continue
                v = r.get(col) or ""
                if not v:
                    continue
                n = v.count(oldv)
                if n == 0:
                    if newv not in v:
                        skipped.append((item, col, "anchor absent", oldv))
                    continue
                if n != 1:
                    skipped.append((item, col, "%d anchors, need 1" % n, oldv))
                    continue
                r[col] = v.replace(oldv, newv)
                done[(item, col)] += 1
                touched = True
        if touched and a.apply:
            with open(f, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA); w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in SCHEMA})

    print("  %s %d cell-edit(s) over %d item(s)"
          % ("applied" if a.apply else "WOULD apply",
             sum(done.values()), len({k[0] for k in done})))
    for (it, col), n in sorted(done.items()):
        print("     %s [%s] x%d" % (it, col, n))
    for it, col, why, oldv in sorted(set(skipped)):
        print("     not applied: %s [%s] %s -- %r" % (it, col, why, oldv[:46]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
