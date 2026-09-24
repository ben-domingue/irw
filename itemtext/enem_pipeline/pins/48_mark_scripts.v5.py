#!/usr/bin/env python3
"""Restore superscripts and subscripts that PDF text extraction flattens.

THE LOSS. A PDF draws an exponent as a smaller span with a raised baseline;
line-based extraction concatenates it, so "6 × 10^23" arrives as "6 × 1023"
and "C10H16O" cannot be told from a word. The numbers change meaning, which
makes this different from a cosmetic glyph issue.

SCOPE, measured rather than assumed. INEP's accessibility (LEDOR) booklets
SPELL notation out, so they contain no superscript spans at all -- the 2019
accessibility booklet has zero. Only the years whose primary source is a
STANDARD colour booklet are affected throughout (2013, 2015, 2016), plus the
handful of items elsewhere that were gap-filled from a standard booklet.

DETECTION is geometric and needs no font knowledge: within one line, a span
whose size is below 85% of the line's body size is a script, and it is a
SUPERSCRIPT if its bottom edge sits clearly above the line's baseline,
a SUBSCRIPT if it does not.

APPLICATION avoids whole-text alignment, which is fragile between extractors.
For each script span we take its LEFT CONTEXT from the same line -- the ~24
characters that precede it -- and rewrite `context + script` as
`context + marker + script` in the shipped cell. A replacement is made only
when that context+script string occurs EXACTLY ONCE in the cell, so an
ambiguous match is skipped and reported rather than guessed at.

NOTATION: `^` for superscript, `_` for subscript, applied to the whole run
(`10^23`, `mol^-1`, `C_10H_16O`). Plain ASCII, searchable, and reversible.

Usage:
  python3 48_mark_scripts.py --year 2013 --pdf <booklet> [--pdf ...] \
        --items-dir <dir> [--apply]
"""
import argparse, collections, csv, glob, os, re, sys

import pymupdf

SCHEMA = ["table","section_id","item","instrument","instructions","section_prompt",
          "item_text","correct_response","option_text","resp","item_text_translated",
          "option_text_translated","instructions_translated","section_prompt_translated",
          "language","resp_raw"]
CTX = 24


def _dedupe_adjacent(marks, v):
    """Drop a marker that merely continues the run just marked.

    "10^-4" arrives as two spans, "-" then "4", so both get a caret and the
    cell reads "10^-^4". If the text between two marks of the same kind has
    no whitespace, the second is inside the first run and is redundant.
    """
    out, last = [], {}
    for pos, kind in sorted(marks):
        prev = last.get(kind)
        if prev is not None and pos > prev and not v[prev:pos].strip() == "" \
                and " " not in v[prev:pos] and "\n" not in v[prev:pos] \
                and pos - prev <= 6:
            continue
        out.append((pos, kind)); last[kind] = pos
    return out


def _loose(t):
    """Regex for t where any whitespace run matches any whitespace run."""
    return r"\s+".join(re.escape(p) for p in t.split())


def scripts_in(pdf):
    """[(left_context, script_text, kind)] for every script span in the file."""
    out = []
    d = pymupdf.open(pdf)
    for i in range(d.page_count):
        for blk in d[i].get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                sp = ln["spans"]
                if len(sp) < 2:
                    continue
                body = max(s["size"] for s in sp)
                base = max(s["bbox"][3] for s in sp)
                run = ""
                for s in sp:
                    t = s["text"]
                    if not t.strip() or s["size"] >= body * 0.85:
                        run += t
                        continue
                    raised = base - s["bbox"][3]
                    kind = "^" if raised > body * 0.15 else (
                           "_" if raised < body * 0.05 else None)
                    if kind is None:
                        run += t
                        continue
                    left = run[-CTX:]
                    # A script never CONTINUES a lowercase word. In 2016 and
                    # 2022 the sequence "f"+"o" is set as two spans of
                    # different size, so the size test read the "o" as a
                    # subscript and produced "conf_orme", "transf_ormação",
                    # "esf_orço" -- 82 broken words. Real scripts attach to a
                    # digit, a symbol or a capital: 10^23, mol^-1, R_s, pK_a,
                    # C_10H_16O. Requiring that the character before is not a
                    # lowercase letter, when the script itself starts
                    # lowercase, keeps all of those and drops the word splits.
                    core = t.strip()
                    lr = left.rstrip()
                    prev = lr[-1:] if lr else ""
                    # A script never CONTINUES a word of the SAME case. The
                    # size test alone produced "conf_orme", "transf_ormação"
                    # (lower->lower, from an f/o span split) and "T_ANTOS",
                    # "PATRIOT_A" (upper->upper). Genuine scripts change case
                    # or follow a digit/symbol: R_s, pK_a, d_A, 10^23, mol^-1,
                    # C_10H_16O. The length test keeps x_i while still
                    # rejecting a real word continuation.
                    if core[:1].isalpha() and prev.isalpha() and \
                            core[:1].islower() == prev.islower():
                        wordlen = len(re.search(r"[A-Za-z\u00c0-\u00ff]*$", lr).group(0))
                        if len(core) >= 2 or wordlen >= 3:
                            run += t
                            continue
                    if left.strip() and t.strip():
                        out.append((left, t, kind))
                    run += t
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", required=True)
    ap.add_argument("--pdf", action="append", required=True)
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    spans = []
    for p in a.pdf:
        spans += scripts_in(p)
    # longest context first: a specific match should win over a generic one
    spans.sort(key=lambda s: -len(s[0]))
    print(f"  {len(spans)} script span(s) found in {len(a.pdf)} booklet(s)")

    applied = collections.Counter()
    ambiguous = collections.Counter()
    for p in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        touched = False
        for r in rows:
            for col in ("item_text", "option_text"):
                v = r.get(col) or ""
                if not v:
                    continue
                # Collect every match against the ORIGINAL cell first, then
                # insert right-to-left. Applying as we go was order-dependent:
                # rewriting "6 x 1023" to "6 x 10^23" destroyed the left context
                # of the very next span ("mol" + "-1"), so the second exponent
                # on the same line was silently lost.
                marks = []
                for left, txt, kind in spans:
                    core = txt.strip()
                    if not core or core not in v or not left.strip():
                        continue
                    # A one-character left context is not an anchor. "T"+"A"
                    # is a legitimate temperature subscript, but it also
                    # matches inside HUERTAS, PATRIOTA, TANTOS. Requiring the
                    # match to START at a token boundary fixes that without
                    # discarding the span: T_A still marks a standalone T A.
                    guard = r"(?<![A-Za-z\u00c0-\u00ff0-9])" if left[:1].isalnum() else ""
                    pat = re.compile(guard + _loose(left) + "(" + _loose(core) + ")")
                    hits = list(pat.finditer(v))
                    # An ALPHABETIC script must also END at a token boundary.
                    # "T"+"A" is a real temperature subscript, but it also sits
                    # at the start of TANTOS, where the "A" is followed by more
                    # letters of the same word. A NUMERIC script may legally be
                    # followed by a letter -- C_10H_16O -- so the test applies
                    # only when the script itself is alphabetic.
                    if core[:1].isalpha():
                        hits = [h for h in hits
                                if not (v[h.end(1):h.end(1)+1].isalpha()
                                        and v[h.end(1):h.end(1)+1].islower()
                                            == core[:1].islower())]
                    if not hits:
                        continue
                    if len(hits) > 1:
                        ambiguous[kind] += 1
                        continue
                    marks.append((hits[0].start(1), kind))
                seen_pos = set()
                marks = _dedupe_adjacent(marks, v)
                for pos, kind in sorted(marks, key=lambda m: -m[0]):
                    if pos in seen_pos:
                        continue
                    seen_pos.add(pos)
                    v = v[:pos] + kind + v[pos:]
                    applied[kind] += 1
                    touched = True
                r[col] = v
        if touched and a.apply:
            with open(p, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA); w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in SCHEMA})
    print(f"  {'applied' if a.apply else 'would apply'}: {dict(applied)}   "
          f"skipped as ambiguous: {dict(ambiguous)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
