#!/usr/bin/env python3
"""Measure, objectively, whether the 2018 decode actually worked.

NAME: the brief called for `18_validate_decode.py`, but a concurrent agent
working on 2021 wrote its own file under that exact name at 10:47 on
2026-09-15. Rather than clobber it -- the precise failure STATUS.md warns
about, "a shared parser was edited mid-flight while five agents were using
it" -- this is the 2018-specific copy. See the report.

A decoder that half-works is worse than none, because its output looks
plausible and no downstream gate reads prose (STATUS.md, "What the gates do NOT
catch"). So this script never says "decoded"; it prints numbers, each against a
known-clean baseline from the SAME exam.

  1. WORD RATE. Fraction of alphabetic tokens (length > 1) present in a
     reference lexicon built from the verified-clean years: 2023 (SHIPPED,
     #1848) and 2019 (175/175 printed keys agree). Same exam, same INEP
     accessibility register, and it includes the English and Spanish LC
     stimuli, which a Portuguese-only dictionary would wrongly score as
     failures. Reported BEFORE and AFTER.

     Reported next to a CEILING, because an absolute rate is not
     interpretable on its own: no finite corpus vocabulary covers another
     text completely, so even perfect text scores well under 100%.
     --control measures booklets that are KNOWN to extract cleanly from a
     year absent from the lexicon (2020 is the right choice when the
     reference is 2019+2023). Whatever those score is the best any decoder
     could reach here, since the remaining shortfall is out-of-sample
     vocabulary, not garbling.

  2. RESIDUE. Control characters (C0 minus \\t\\n\\r), /gNNN and (cid:NNN)
     glyph tokens, and U+FFFD. Any survivor is counted and named.

  3. ACCENT PROFILE. Rate per 10,000 characters of ã ç õ é ê á í ó ú (plus
     â ô à ü) against the clean years. This is the check that catches an
     off-by-one in the glyph table -- exactly the live risk here, since
     Arial's glyph order diverges from the standard Macintosh ordering from
     CID 172 on. A one-slot error shows as a deficit in one accent and a
     matching surplus in its neighbour, which a word rate can miss.

  4. Answer-key agreement is NOT measured here; that is 16_verify_gabarito.py,
     run separately, and it must still report 174/174 for 2018.

Usage:
  python3 18_validate_decode_2018.py --pdf <booklet.pdf> [--pdf ...] \
      [--control <clean.pdf> ...] [--json out.json]
  python3 18_validate_decode_2018.py --ref-only
"""
import argparse
import collections
import csv
import glob
import json
import logging
import os
import re
import sys
import unicodedata
import warnings

logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
_dec = importlib.import_module("17_decode_2018")

REF_GLOBS = [
    "/home/users/mazzafe/irw/itemtext/itemtables/batch_enem_2023/enem_2023_1mil_*__items.csv",
    "/scratch/users/mazzafe/itemtext_years/2019/enem_2019_1mil_*__items.csv",
]
TEXT_COLS = ("instrument", "instructions", "section_prompt", "item_text", "option_text")
ACCENTS = "ãçõéêáíóúâôàü"
CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
# A bare glyph reference, NOT a URL path. "http://g1.globo.com" appears in a
# 2018 CN credit line and matched the naive /g\d+ pattern, reporting a
# phantom residue; require the slash not to be part of a URL or word.
GLYPHTOK = re.compile(r"(?<![\w/:.])/g\d+|\(cid:\d+\)")
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)
LIG = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl",
       "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"}


def expand_lig(s):
    for k, v in LIG.items():
        s = s.replace(k, v)
    return s


def words(text):
    return [w.lower() for w in WORD.findall(expand_lig(text)) if len(w) > 1]


def load_reference():
    lex, acc, total = collections.Counter(), collections.Counter(), 0
    files = []
    for g in REF_GLOBS:
        files.extend(sorted(glob.glob(g)))
    if not files:
        sys.exit("no reference CSVs found; checked:\n  " + "\n  ".join(REF_GLOBS))
    csv.field_size_limit(10 ** 8)
    # Dedupe distinct values: `instructions`/`instrument` repeat on every row
    # of a table; counting them ~180x each would skew the accent baseline
    # towards the cover page instead of the item text.
    seen = set()
    for fn in files:
        with open(fn, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                for col in TEXT_COLS:
                    v = (row.get(col) or "").strip()
                    if not v or v == "NA" or (col, v) in seen:
                        continue
                    seen.add((col, v))
                    for w in words(v):
                        lex[w] += 1
                    for ch in v:
                        total += 1
                        if ch.lower() in ACCENTS:
                            acc[ch.lower()] += 1
    prof = {a: 10000.0 * acc[a] / total for a in ACCENTS} if total else {}
    return lex, prof, total, files


def pdf_text(path):
    from pypdf import PdfReader
    return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)


def measure(text, lex):
    toks = words(text)
    known = [t for t in toks if t in lex]
    ctrl = CTRL.findall(text)
    accs = collections.Counter(ch.lower() for ch in text if ch.lower() in ACCENTS)
    n, nc = len(toks), len(text)
    return {
        "chars": nc, "tokens": n, "known": len(known),
        "word_rate": (len(known) / n) if n else 0.0,
        "ctrl": len(ctrl),
        "ctrl_kinds": sorted({"0x%02x" % ord(c) for c in ctrl})[:12],
        "glyph_tokens": len(GLYPHTOK.findall(text)),
        "fffd": text.count("�"),
        "accents": {a: 10000.0 * accs[a] / nc for a in ACCENTS} if nc else
                   {a: 0.0 for a in ACCENTS},
        "unknown_top": collections.Counter(
            t for t in toks if t not in lex).most_common(20),
    }


def _wavg(ms, x):
    C = sum(m["chars"] for m in ms) or 1
    return sum(m["accents"][x] * m["chars"] for m in ms) / C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", action="append", default=[])
    ap.add_argument("--control", action="append", default=[])
    ap.add_argument("--json")
    ap.add_argument("--ref-only", action="store_true")
    ap.add_argument("--tmpdir", default="/scratch/users/mazzafe/itemtext_years/2018/work")
    a = ap.parse_args()

    lex, prof, refchars, reffiles = load_reference()
    print("REFERENCE (verified-clean 2019 + 2023 item text)")
    print("  files      : %d" % len(reffiles))
    print("  chars      : %d (distinct values only)" % refchars)
    print("  vocabulary : %d distinct tokens" % len(lex))
    print("  accents per 10k chars:")
    print("    " + "  ".join("%s=%.1f" % (x, prof[x]) for x in ACCENTS))

    ceil, cacc = None, None
    if a.control:
        print("\nCONTROL: known-clean booklets from a year absent from the lexicon")
        ms = []
        for p in a.control:
            m = measure(pdf_text(p), lex)
            ms.append(m)
            print("  %-46s tokens=%6d wordrate=%5.1f%% ctrl=%4d"
                  % (os.path.basename(p)[:46], m["tokens"],
                     100 * m["word_rate"], m["ctrl"]))
        T = sum(m["tokens"] for m in ms); K = sum(m["known"] for m in ms)
        ceil = K / T if T else None
        cacc = {x: _wavg(ms, x) for x in ACCENTS}
        print("  CONTROL CEILING: %.1f%%  (%d/%d tokens)" % (100 * ceil, K, T))
        print("  control accents per 10k chars:")
        print("    " + "  ".join("%s=%.1f" % (x, cacc[x]) for x in ACCENTS))

    if a.ref_only or not a.pdf:
        return 0

    os.makedirs(a.tmpdir, exist_ok=True)
    results, agg = {}, {"before": [], "after": [], "textpath": []}
    for p in a.pdf:
        name = os.path.basename(p)
        print("\n" + "=" * 76 + "\n" + name + "\n" + "=" * 76)
        raw = pdf_text(p)
        tmp = os.path.join(a.tmpdir, "_validate_tmp.pdf")
        _dec.repair_pdf(p, tmp, verbose=False)
        rep = pdf_text(tmp)
        os.remove(tmp)
        r = {"before": measure(raw, lex), "after": measure(rep, lex),
             "textpath": measure(_dec.decode_text(raw), lex)}
        results[name] = r
        print("  %-10s %8s %7s %7s %9s %6s %6s %6s"
              % ("stage", "chars", "tokens", "known", "wordrate", "ctrl", "FFFD", "glyph"))
        for k in ("before", "after", "textpath"):
            m = r[k]; agg[k].append(m)
            print("  %-10s %8d %7d %7d %8.1f%% %6d %6d %6d"
                  % (k, m["chars"], m["tokens"], m["known"], 100 * m["word_rate"],
                     m["ctrl"], m["fffd"], m["glyph_tokens"]))
        if r["after"]["ctrl"]:
            print("  !! residual control chars: %s" % r["after"]["ctrl_kinds"])
        print("  unknown-token top AFTER: %s"
              % [t for t, _ in r["after"]["unknown_top"][:12]])

    print("\n" + "=" * 76 + "\nCORPUS TOTAL (all booklets)\n" + "=" * 76)
    tot = {}
    for k in ("before", "after", "textpath"):
        ms = agg[k]
        T = sum(m["tokens"] for m in ms); K = sum(m["known"] for m in ms)
        tot[k] = {"chars": sum(m["chars"] for m in ms), "tokens": T, "known": K,
                  "word_rate": K / T if T else 0,
                  "ctrl": sum(m["ctrl"] for m in ms),
                  "fffd": sum(m["fffd"] for m in ms),
                  "glyph_tokens": sum(m["glyph_tokens"] for m in ms),
                  "accents": {x: _wavg(ms, x) for x in ACCENTS}}
        t = tot[k]
        print("  %-10s chars=%7d tokens=%6d known=%6d wordrate=%5.1f%% ctrl=%5d FFFD=%3d glyph=%d"
              % (k, t["chars"], T, K, 100 * t["word_rate"], t["ctrl"],
                 t["fffd"], t["glyph_tokens"]))

    print("\n  ACCENT PROFILE per 10k chars  (deficit/surplus catches an off-by-one)")
    print("    %-3s %8s %8s %8s %8s %s" % ("", "before", "after", "ref", "control", "after/ref"))
    for x in ACCENTS:
        print("    %-3s %8.2f %8.2f %8.2f %8s %9.2f"
              % (x, tot["before"]["accents"][x], tot["after"]["accents"][x], prof[x],
                 ("%.2f" % cacc[x]) if cacc else "-",
                 (tot["after"]["accents"][x] / prof[x]) if prof[x] else 0))

    wr = tot["after"]["word_rate"]
    print("\n  VERDICT")
    print("    word rate  before %.1f%%  ->  after %.1f%%"
          % (100 * tot["before"]["word_rate"], 100 * wr))
    print("    residue    ctrl %d  glyph %d  FFFD %d"
          % (tot["after"]["ctrl"], tot["after"]["glyph_tokens"], tot["after"]["fffd"]))
    if ceil:
        frac = wr / ceil
        print("    ceiling    %.1f%% (clean control)  ->  decode reaches %.1f%% of achievable"
              % (100 * ceil, 100 * frac))
        print("    %s" % ("CONVINCING: indistinguishable from a clean booklet"
                          if frac > 0.97 else
                          "NOT CONVINCING: materially short of the clean-booklet ceiling"))
    else:
        print("    no --control given; absolute >85%%: %s" % ("PASS" if wr > 0.85 else "FAIL"))
    if a.json:
        json.dump({"reference_accents": prof, "control_ceiling": ceil,
                   "control_accents": cacc, "per_pdf": results, "total": tot},
                  open(a.json, "w"), indent=1)
        print("    wrote %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
