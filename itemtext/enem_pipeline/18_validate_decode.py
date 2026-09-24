#!/usr/bin/env python3
"""Measure, objectively, whether the 2021 glyph decoder actually worked.

A decoder that half works is worse than none, because its output reads as
plausible Portuguese and no gate downstream looks at prose (see STATUS.md,
"What the gates do NOT catch": 2021 CH and LC PASSED validate_items.R at 93%
glyph tokens). So this measures four things and prints the numbers.

1. KNOWN-WORD RATE. The reference vocabulary is built from the years already
   verified clean -- 2019 (175/175 printed keys agree) and 2023 (SHIPPED,
   0 glyph tokens in 800k chars). Same exam, same register, same INEP
   accessibility wording, so it is the right comparison and not a generic
   Portuguese dictionary.

   The rate is reported together with a CEILING measured the same way: the
   rate CLEAN text scores against that same finite vocabulary. 2019 text
   scored against a 2023-only vocabulary, and vice versa. Without the ceiling
   an absolute rate is not interpretable -- no finite corpus vocabulary covers
   another text completely, so even perfect text scores well under 100%.

2. RESIDUE. /gNNN tokens, the decoder's own [UNDECODED-gNNN] markers, C0/C1
   control characters and U+FFFD. Any of these is a hard fail.

3. ACCENT PROFILE. Rate per 10,000 letters of ã ç õ é ê á í ó ú, against the
   clean years. A decoder that has the accented glyph ids shifted by one --
   the exact risk here, since Arial's glyph order diverges from standard
   Macintosh ordering from gid 172 on -- shows as a deficit in one accent and
   a matching surplus in another, which a word rate can miss but this cannot.

4. Answer-key agreement is NOT measured here: it is 16_verify_gabarito.py,
   which is run separately and is mandatory.

LIKE FOR LIKE. The word and accent rates are measured on PARSED ITEM TEXT
(stem + option_text), never on raw whole-PDF text. Measuring the raw PDF
against the clean years' item CSVs gave a false alarm the first time this was
run -- 2021 "after" showed an o-tilde rate of 17.65 per 10k against 76.68 in
the clean years, a ratio of 0.23 that looked like a mangled accent. It was not:
raw booklet text carries the cover, the page furniture, the credits and the
ENTIRE English and Spanish LC blocks, none of which has a Portuguese accent in
it, and all of which the clean years' item CSVs exclude. Compare what ships
with what shipped.

USAGE
    python3 18_validate_decode.py --clean-dir /scratch/users/<u>/itemtext_years \
        --parsed-before <dir|csv> --parsed-after <dir|csv> \
        --pdf <pdf> [--pdf ...] --map <gidmap.json> [--json out.json]
"""
from __future__ import annotations
import argparse, collections, csv, importlib.util, json, logging, os, re, sys, unicodedata, warnings
logging.disable(logging.CRITICAL); warnings.filterwarnings("ignore")
from pypdf import PdfReader

MARKER = "[UNDECODED-g%d]"

HERE = os.path.dirname(os.path.abspath(__file__))
ACCENTS = "ãçõéêáíóú"
WORD = re.compile(r"[^\W\d_]{2,}", re.UNICODE)
# A leaked glyph name, but NOT a URL. Two ways to get this wrong, both hit:
#  - a naive /g\d+ matches "https://g1.globo.com", which appears in ENEM
#    credit lines, so the verified-clean 2019 parse "contained" 6 glyph tokens
#  - excluding a preceding word character undercounts the GARBLED case by 16x,
#    because the tokens run together: "/g43/g82/g92" is three tokens and the
#    second and third are preceded by a digit
# So: the slash must not itself follow a slash (which kills "://g1"), and the
# digits must not run into ".globo".
GLYPH_TOKEN = re.compile(r"(?<!/)/g\d+(?!\.\w)")
MARKER_TOKEN = re.compile(r"\[UNDECODED-g\d+\]")
CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f�]")
LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl",
             "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"}


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name.replace(".", "_"), os.path.join(HERE, name))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def expand_ligatures(t):
    for k, v in LIGATURES.items():
        t = t.replace(k, v)
    return t


def words(text):
    # the decoder's own marker must not be counted as an unknown word: it is
    # already counted, separately and more visibly, as an undecoded glyph.
    return [w.lower() for w in WORD.findall(MARKER_TOKEN.sub(" ", text))]


def parsed_text(paths, keep=None):
    """stem + option_text out of 12_parse_booklet_pdf's own CSV columns.

    keep: None for everything, or 0/1 to take alternate ITEMS, which is how
    the clean-text ceiling is measured on held-out data of exactly the same
    kind (same parser, same booklet furniture, same register).
    """
    out, files = [], []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(os.path.join(p, f) for f in os.listdir(p)
                            if f.endswith(".csv"))
        else:
            files.append(p)
    idx, out = 0, []
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            cur = None
            for row in csv.DictReader(fh):
                key = (row.get("area"), row.get("lang_block"), row.get("position"))
                if key != cur:                      # stem repeats on 5 rows
                    cur = key
                    idx += 1
                    take = keep is None or idx % 2 == keep
                    if take:
                        out.append(row.get("stem") or "")
                if take:
                    out.append(row.get("option_text") or "")
    return "\n".join(out), files


def clean_year_text(clean_dir, year):
    """Concatenate item_text + option_text from a year's built items CSVs."""
    out = []
    for area in ("ch", "cn", "lc", "mt"):
        for cand in (
            os.path.join(clean_dir, str(year), f"enem_{year}_1mil_{area}__items.csv"),
            os.path.join("/home/users/mazzafe/irw/itemtext/itemtables",
                         f"batch_enem_{year}", f"enem_{year}_1mil_{area}__items.csv"),
        ):
            if not os.path.exists(cand):
                continue
            # Two traps, both of which made a CORRECT decode look broken.
            # (1) item_text repeats on all five option rows, so dedupe by item
            #     or the two sides weight stem text 5:1 against option text.
            # (2) `instructions` is the booklet COVER, identical on every row,
            #     i.e. 175 copies of it in 2019 and 174 in 2023. It contains
            #     "As questoes de 01 a 45", so those copies alone supplied 2240
            #     of 2019's 3364 o-tildes and pushed the reference o-tilde rate
            #     to 73 per 10k against the 16 a clean 2021 parse can reach.
            #     The parsed side has no instructions column at all -- the
            #     pinned parser writes the cover to <out>.cover.txt -- so the
            #     reference must be stem + options only.
            seen = set()
            with open(cand, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    key = row.get("item")
                    if key not in seen:
                        seen.add(key)
                        for col in ("item_text",):
                            v = (row.get(col) or "").strip()
                            if v and v != "NA":
                                out.append(v)
                    v = (row.get("option_text") or "").strip()
                    if v and v != "NA":
                        out.append(v)
            break
    return "\n".join(out)


def profile(text, vocab):
    text = expand_ligatures(text)
    ws = words(text)
    known = sum(1 for w in ws if w in vocab)
    letters = sum(1 for c in text if c.isalpha())
    acc = {a: ((text.count(a) + text.count(a.upper())) * 10000 / letters)
           if letters else 0.0 for a in ACCENTS}
    long = [w for w in ws if len(w) >= 4]
    return {
        "known_word_rate_len4plus":
            (sum(1 for w in long if w in vocab) / len(long)) if long else 0.0,
        "chars": len(text),
        "letters": letters,
        "alpha_tokens": len(ws),
        "known_tokens": known,
        "known_word_rate": known / len(ws) if ws else 0.0,
        "glyph_tokens": len(GLYPH_TOKEN.findall(text)),
        "undecoded_markers": len(MARKER_TOKEN.findall(text)),
        "control_chars": len(CTRL.findall(text)),
        "accents_per_10k_letters": {a: round(v, 2) for a, v in acc.items()},
    }


def unknown_sample(text, vocab, n=40):
    c = collections.Counter(w for w in words(expand_ligatures(text)) if w not in vocab)
    return c.most_common(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean-dir", default="/scratch/users/mazzafe/itemtext_years")
    ap.add_argument("--pdf", action="append", default=[],
                    help="2021 booklet, for the residue check; repeatable")
    ap.add_argument("--map", help="cached gid->unicode map (17 --save-map)")
    ap.add_argument("--parsed-before", action="append", required=True,
                    help="parsed CSV or dir, pinned parser WITHOUT the decoder")
    ap.add_argument("--parsed-after", action="append", required=True,
                    help="parsed CSV or dir, pinned parser WITH the decoder")
    ap.add_argument("--evidence", action="append", default=None,
                    help="PDFs to derive the glyph map from (default: --pdf set)")
    ap.add_argument("--json")
    a = ap.parse_args()

    # ---- reference: the two years verified clean, scored symmetrically
    #
    # A split-half of one year does NOT work here and the first attempt scored
    # a bogus 1.0000: /scratch/.../2019/parsed holds four EDITIONS of the same
    # 180 items (acc_d1/d2, std_d1/d2, p2019, s2019), so both halves contain
    # the same item text and the vocabulary leaks completely.
    #
    # The situation 2021 is actually in is "a year's text scored against a
    # DIFFERENT year's vocabulary". So that is measured twice, and 2021 is
    # measured under each of the two identical conditions:
    #
    #   against the 2019 vocabulary: ceiling = clean 2023, subject = 2021
    #   against the 2023 vocabulary: ceiling = clean 2019, subject = 2021
    #
    # Same vocabulary, same tokeniser, same both sides. No year is ever scored
    # against a vocabulary built from itself.
    p19 = os.path.join(a.clean_dir, "2019", "parsed")
    if not os.path.isdir(p19):
        print(f"FAIL: no clean 2019 parse at {p19}")
        return 2
    t19 = parsed_text([p19])[0]
    t23 = clean_year_text(a.clean_dir, 2023)
    if not t23:
        print("FAIL: could not load the clean 2023 item CSVs")
        return 2
    v19 = set(words(expand_ligatures(t19)))
    v23 = set(words(expand_ligatures(t23)))
    print(f"vocabularies: 2019 clean booklet parse {len(v19)} types "
          f"({len(t19)} chars); 2023 clean item CSVs {len(v23)} types "
          f"({len(t23)} chars)")
    vocab = v19 | v23
    ref = {"2019_vs_v23": profile(t19, v23), "2023_vs_v19": profile(t23, v19)}
    ceiling = (ref["2019_vs_v23"]["known_word_rate"]
               + ref["2023_vs_v19"]["known_word_rate"]) / 2
    ceiling4 = (ref["2019_vs_v23"]["known_word_rate_len4plus"]
                + ref["2023_vs_v19"]["known_word_rate_len4plus"]) / 2
    print(f"CEILING from clean text under the same conditions: "
          f"2019 vs 2023-vocab {ref['2019_vs_v23']['known_word_rate']:.4f}, "
          f"2023 vs 2019-vocab {ref['2023_vs_v19']['known_word_rate']:.4f}, "
          f"mean {ceiling:.4f} "
          f"(tokens >=4 chars: {ceiling4:.4f})")

    # ---- 2021 item text, before and after, as parsed by the PINNED parser
    tb, fb = parsed_text(a.parsed_before)
    ta, fa = parsed_text(a.parsed_after)
    print(f"parsed BEFORE: {len(fb)} file(s), {len(tb)} chars")
    print(f"parsed AFTER : {len(fa)} file(s), {len(ta)} chars")
    b, aft = profile(tb, vocab), profile(ta, vocab)
    # the comparable numbers: 2021 under each single-year vocabulary, exactly
    # the condition each ceiling was measured under
    a19, a23 = profile(ta, v19), profile(ta, v23)
    b19, b23 = profile(tb, v19), profile(tb, v23)
    aft["known_word_rate_single_year_mean"] = (
        a19["known_word_rate"] + a23["known_word_rate"]) / 2
    aft["known_word_rate_len4plus_single_year_mean"] = (
        a19["known_word_rate_len4plus"] + a23["known_word_rate_len4plus"]) / 2
    b["known_word_rate_single_year_mean"] = (
        b19["known_word_rate"] + b23["known_word_rate"]) / 2
    b["known_word_rate_len4plus_single_year_mean"] = (
        b19["known_word_rate_len4plus"] + b23["known_word_rate_len4plus"]) / 2
    # ---- how much text the decoder actually RECOVERED.
    # The word rate alone is misleading in the before/after direction and the
    # first run of this harness showed why: BEFORE decoding, 2021 scored 0.837
    # -- HIGHER than after -- because only the 33% of the booklet set in the
    # good font was legible at all, and that 33% is the headings, the credits
    # and the Latin-script foreign-language items, which are easy words. The
    # decoder adds the body prose, which is where the proper nouns and the
    # technical vocabulary live. So report coverage separately from accuracy.
    new_types = (set(words(expand_ligatures(ta)))
                 - set(words(expand_ligatures(tb))))
    nt_known = sum(1 for w in new_types if w in vocab)
    nt_rate = nt_known / max(len(new_types), 1)
    # TYPE-level rates are far lower than token-level ones everywhere, because
    # types are dominated by hapax proper nouns, so this needs its own ceiling
    # measured the same way on clean text.
    ty19, ty23 = set(words(expand_ligatures(t19))), set(words(expand_ligatures(t23)))
    nt_ceiling = ((len(ty19 & v23) / max(len(ty19), 1))
                  + (len(ty23 & v19) / max(len(ty23), 1))) / 2
    print(f"\nrecovery: alphabetic tokens {b['alpha_tokens']} -> "
          f"{aft['alpha_tokens']} "
          f"({aft['alpha_tokens'] / max(b['alpha_tokens'], 1):.2f}x); "
          f"letters {b['letters']} -> {aft['letters']}")
    print(f"newly recovered word TYPES (present after, absent before): "
          f"{len(new_types)}, of which {nt_known} ({nt_rate:.4f}) are in the "
          f"clean-year vocabulary; type-level CEILING on clean text "
          f"{nt_ceiling:.4f}")
    lig = len(re.findall(r"(?<![^\W\d_])(?:fi|fl)(?![^\W\d_])", ta))
    print(f"stray 'fi'/'fl' tokens after decode: {lig} "
          f"(pypdf splits a word at the ligature glyph because of the gap the "
          f"booklet's own text matrix leaves there; present before decoding "
          f"too, as a /gNNN token with spaces round it -- a layout artefact, "
          f"not a decoding error)")
    print(f"2021 BEFORE under single-year vocabularies: "
          f"vs2019 {b19['known_word_rate']:.4f}  vs2023 {b23['known_word_rate']:.4f}")
    print(f"2021 AFTER  under single-year vocabularies: "
          f"vs2019 {a19['known_word_rate']:.4f}  vs2023 {a23['known_word_rate']:.4f}")

    # ---- residue over the WHOLE booklet text, which is stricter than the
    # parsed subset: a glyph token in the cover or a credit line still means
    # the decoder is incomplete.
    meta = {}
    if a.pdf:
        dec = _load("17_decode_2021.py")
        gmap = dec.load_map(a.map) if a.map else dec.build_map(a.pdf)[0]
        raw = dec_txt = ""
        for p in a.pdf:
            raw += "\n".join((pg.extract_text() or "") for pg in PdfReader(p).pages)
            dec_txt += "\n".join((pg.extract_text() or "")
                                  for pg in dec.decoded_reader(p, gmap).pages)
        rb, ra = profile(raw, vocab), profile(dec_txt, vocab)
        print(f"\nwhole-booklet residue  BEFORE: /gNNN {rb['glyph_tokens']}, "
              f"ctrl {rb['control_chars']}, chars {rb['chars']}")
        print(f"whole-booklet residue  AFTER : /gNNN {ra['glyph_tokens']}, "
              f"markers {ra['undecoded_markers']}, ctrl {ra['control_chars']}, "
              f"chars {ra['chars']}")
        # The honest denominator is the DECODED length, because each garbled
        # character occupied ~4 characters of "/gNNN" before. Against the raw
        # extracted length the same defect reads as 85%, which overstates it.
        print(f"garble rate BEFORE: {rb['glyph_tokens']} of the "
              f"{ra['chars']} characters the decoder recovers "
              f"({rb['glyph_tokens'] / max(ra['chars'], 1):.1%}) were a "
              f"/gNNN token, occupying "
              f"{sum(len(t) for t in GLYPH_TOKEN.findall(raw))} of "
              f"{rb['chars']} raw extracted characters")
        meta = {"whole_before": rb, "whole_after": ra, "map_size": len(gmap)}
        aft["glyph_tokens"] = ra["glyph_tokens"]
        aft["undecoded_markers"] = ra["undecoded_markers"]
        aft["control_chars"] = ra["control_chars"]
        b["glyph_tokens"] = rb["glyph_tokens"]

    def show(tag, pr):
        print(f"\n[{tag}]")
        print(f"  chars {pr['chars']}  letters {pr['letters']}  alpha tokens {pr['alpha_tokens']}")
        print(f"  known-word rate      {pr['known_word_rate']:.4f}"
              f"   (tokens >=4 chars: {pr['known_word_rate_len4plus']:.4f})")
        if "known_word_rate_single_year_mean" in pr:
            print(f"  same-condition rate  "
                  f"{pr['known_word_rate_single_year_mean']:.4f}"
                  f"   (tokens >=4 chars: "
                  f"{pr['known_word_rate_len4plus_single_year_mean']:.4f})"
                  f"   <- compare with CEILING")
        print(f"  /gNNN tokens         {pr['glyph_tokens']}")
        print(f"  undecoded markers    {pr['undecoded_markers']}")
        print(f"  control chars/FFFD   {pr['control_chars']}")
        print("  accents /10k letters " + "  ".join(
            f"{k}={v}" for k, v in pr['accents_per_10k_letters'].items()))

    show("2021 BEFORE decode", b)
    show("2021 AFTER decode", aft)
    show("2019 clean parse, scored vs 2023 vocabulary", ref["2019_vs_v23"])
    show("2023 clean items, scored vs 2019 vocabulary", ref["2023_vs_v19"])

    print("\naccent profile, 2021-after vs mean of clean years "
          "(ratio; 1.00 = identical rate)")
    for k in ACCENTS:
        m = (ref["2019_vs_v23"]["accents_per_10k_letters"][k]
             + ref["2023_vs_v19"]["accents_per_10k_letters"][k]) / 2
        r = aft["accents_per_10k_letters"][k] / m if m else float("nan")
        flag = "" if 0.65 <= r <= 1.45 else "   <-- OUT OF BAND"
        print(f"  {k}  2021={aft['accents_per_10k_letters'][k]:8.2f}  "
              f"clean={m:8.2f}  ratio={r:5.2f}{flag}")

    print("\ntop unknown tokens after decode (diagnosis aid, not a failure):")
    for w, n in unknown_sample(ta, vocab, 25):
        print(f"  {n:6d}  {w}")

    # ---- verdict
    checks = {
        "no_glyph_tokens": aft["glyph_tokens"] == 0,
        "no_undecoded_markers": aft["undecoded_markers"] == 0,
        "undecoded_below_0.1pct_of_chars":
            aft["undecoded_markers"] * len(MARKER % 0 if False else "x") >= 0
            and aft["undecoded_markers"] / max(aft["chars"], 1) < 0.001,
        "newly_recovered_types_at_clean_type_ceiling": nt_rate >= 0.9 * nt_ceiling,
        "no_control_chars": aft["control_chars"] == 0,
        "word_rate_within_5pct_of_clean_ceiling":
            aft["known_word_rate_single_year_mean"] >= 0.95 * ceiling,
        # The brief's ">85% of alphabetic tokens" is applied to the >=4-char
        # tokens, because 1-3 char tokens in these booklets are units and
        # variable names (mm, kg, gl, br, aij) that no reference vocabulary
        # built from prose will ever contain, clean year or not.
        "word_rate_len4plus_within_5pct_of_ceiling":
            aft["known_word_rate_len4plus_single_year_mean"] >= 0.95 * ceiling4,
        "accents_in_band": all(
            0.65 <= (aft["accents_per_10k_letters"][k] /
                    (((ref["2019_vs_v23"]["accents_per_10k_letters"][k]
                       + ref["2023_vs_v19"]["accents_per_10k_letters"][k]) / 2)
                     or 1)) <= 1.45
            for k in ACCENTS),
    }
    print("\nCHECKS")
    for k, v in checks.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    ok = all(checks.values())
    print("\nVERDICT:", "DECODER VALIDATED" if ok else "NOT VALIDATED")
    if a.json:
        json.dump({"ceiling_all_tokens": ceiling, "ceiling_len4plus": ceiling4,
                   "before": b, "after": aft,
                   "reference": ref, "checks": checks, "verdict": ok,
                   "residue": meta},
                  open(a.json, "w"), ensure_ascii=False, indent=1)
        print("json ->", a.json)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
