#!/usr/bin/env python3
"""Parse an ENEM booklet PDF into (area, language block, position, stem, options).

The PDF path for 2013-2022 and for items the accessibility booklet swaps away.
Emits a CSV for 13_join.py to map position -> CO_ITEM. Does NOT touch item
codes: this file knows nothing about CO_ITEM, which is EXTRACTION_RULES.md R0.

WHAT MAKES THIS FIDDLY, all observed in real booklets:

1. Markers are title-case "Questão 01", not "QUESTÃO 01", and the number
   RESTARTS per area. So the position of an item is only meaningful together
   with its area, which is read from the section headers.

2. LC carries 50 items over 45 positions: positions 1-5 appear twice, once per
   foreign language, announced by "Questões de 01 a 05 (opção inglês/espanhol)".
   Both blocks ship; TP_LINGUA disambiguates them at the join.

3. AN OPTION LINE CANNOT BE FOUND BY "starts with A-E". In 2019 LC item 5 the
   stem contains the line "A canção, muitas vezes, é uma forma de manifestar"
   -- a stem line beginning "A ". Taking the first ^[A-E] match would cut the
   stem in half and mislabel the options. Instead we find the LAST run of five
   candidate lines whose letters read exactly A,B,C,D,E in order, which is the
   option block by construction: the five printed options always close an item
   and always appear in order.

4. Options wrap over several lines, so an option's text runs to the next
   option's start line.

A parse that cannot find five options in order for an item is reported, never
guessed at. Usage:
  python3 12_parse_booklet_pdf.py <pdf> --year Y --out items.csv [--expect N]
"""
import argparse, csv, logging, os, re, sys, warnings
logging.disable(logging.CRITICAL); warnings.filterwarnings("ignore")
from pypdf import PdfReader

AREA_HEADERS = [
    (re.compile(r"LINGUAGENS,?\s+C[ÓO]DIGOS", re.I), "LC"),
    (re.compile(r"CI[ÊE]NCIAS\s+HUMANAS", re.I), "CH"),
    (re.compile(r"CI[ÊE]NCIAS\s+DA\s+NATUREZA", re.I), "CN"),
    (re.compile(r"MATEM[ÁA]TICA", re.I), "MT"),
]
LANG_BLOCK = re.compile(r"op[çc][ãa]o\s*:?\s*(ingl[êe]s|espanhol)", re.I)
# The booklet states the block's range itself: "Questões de 91 a 95 (opção
# inglês)". Read it, rather than assuming LC sits at printed 1-5. In 2013, 2015
# and 2016 the day order is CH/CN then LC/MT, so LC's language block is at
# printed 91-95 and a "pos <= 5" guard never fires -- both language versions
# then land on the same position and the item ships TEN option rows with two
# resp=1, which validate_items.R passes (the 2018 LC failure).
LANG_RANGE = re.compile(
    r"Quest[õo]es\s+de\s+(\d+)\s+a\s+(\d+)\s*\(?\s*op[çc][ãa]o\s*:?\s*(ingl[êe]s|espanhol)", re.I)
# Trailing punctuation occurs: 2017 day 2 prints "QUESTÃO 108 ." and a strict
# end-anchor skipped it, which did NOT show up as a parse failure -- the item's
# text was absorbed into its predecessor and only the --expect count differed.
MARKER = re.compile(r"^\s*Quest[ãa]o\s+(\d{1,3})\s*[.;:]?\s*$", re.I)
# Two option layouts occur, both in the same corpus:
#   "A pela morte precoce de um amigo jovem."   letter and text on one line
#   "A" then the text on the following lines     letter alone (2019 MT 166, 177)
# The second is how the accessibility booklet sets a long option, including the
# "Descrição do gráfico:" blocks where INEP describes an option that is a figure.
OPT_INLINE = re.compile(r"^\s*([A-E])\s+(\S.*)$")
OPT_ALONE = re.compile(r"^\s*([A-E])\s*$")
# INEP writes "Descrição do gráfico:" / "Descrição da figura:" etc. into the
# accessibility booklet. Its presence in an option body is positive evidence
# that the body is real option text, not a figure's interior leaking in.
# Must match INEP's BLOCK HEADER, not the word in prose. "Descrição da imagem :"
# and "Descrição do gráfico:" are headers; "baseada na descrição dos hábitos
# alimentares" is ordinary option text. A loose pattern cost a real miss: 2019
# LC 76167 has 4,275 chars of stimulus (TEXTO III + "Descrição da imagem :")
# orphaned into option E, and the move was blocked because option A's prose
# matched the exclusion guard. The colon is what distinguishes them.
# INEP's figure-description block, as a PARAGRAPH HEADER. Four things this has
# to get right, each of which it got wrong before:
#  - PLURALS. `d[oaes]\b` cannot match "dos"/"das": after "do" the \b fails on
#    the following "s". So "Descricao das figuras:" and "Descricao dos
#    graficos:" never matched and their blocks stayed stuck in option E.
#  - WRAPPING. The head can break across a line ("...de cinco colunas e cinco
#    \nlinhas:"), so it must NOT exclude \n. The old [^\n:] could not cross it.
#  - LENGTH. 40 characters was too short for INEP's real headers.
#  - CASE AND POSITION. The block is its own paragraph and starts with a
#    capital; ordinary option prose uses lowercase "descricao" mid-sentence.
#    Requiring a line start and a capital D is what keeps 2017 LC 90020
#    ("descricao do espaco, como em: ...") from being mistaken for a block --
#    the old pattern DID match that one, which is why the colon alone was not
#    a sufficient guard (trap 27).
DESCRICAO = re.compile(r"(?m)^[ \t]*Descri[\u00e7c][\u00e3a]o\s+d(?:o|a|e)s?\b[^:]{0,90}:")
# A doubled letter with no separator, e.g. "AA Descrição do esquema:". 2022's
# text layer emits every option letter twice; without this the item yields no
# candidates at all and is rejected (3 MT and 4 CN items in 2022).
OPT_DOUBLE = re.compile(r"^\s*([A-E])\1\s*(\S.*)$")
# "AA" alone on its line, and lines that are only doubled letters ("AA BB CC").
OPT_DOUBLE_ALONE = re.compile(r"^\s*([A-E])\1\s*$")
OPT_DOUBLE_MULTI = re.compile(r"^\s*(?:([A-E])\1\s*){2,}$")
# trailing page furniture that must not be swallowed into the last option
FURNITURE = re.compile(
    r"^\s*(LINGUAGENS|CI[ÊE]NCIAS|MATEM[ÁA]TICA|Quest[õo]es de|\d{1,3}"
    r"|\*[0-9A-Z]+\*"                      # barcode, e.g. *020325AZ7*
    r"|(?:ENEM\s*\d{4}\s*){2,}"            # repeated watermark
    r"|(?:LC|CH|CN|MT)\s*-\s*\d.*Caderno.*"  # running head
    r"|[A-Z ,ÊÁÓÇ]{8,})\s*$")


def page_lines(pdf):
    for pg in PdfReader(pdf).pages:
        for ln in (pg.extract_text() or "").split("\n"):
            yield ln


def segment(pdf):
    """Walk the lines once, tracking area and language block, and cut at markers.

    Also returns the cover: everything before the first item marker. R7 needs it
    for `instructions`, and 13_join.py previously left that column blank on
    every row of every year because nothing ever produced it."""
    area, lang, cur, out, cover = None, None, None, [], []
    lang_lo = lang_hi = None   # the block's printed range, read from its header
    for ln in page_lines(pdf):
        for rx, a in AREA_HEADERS:
            t = ln.strip()
            if not (rx.search(ln) and len(t) < 60):
                continue
            # A section header is SET IN CAPITALS; item prose is not. Without
            # this, the CH stem line "astronomia e matemática, além de grande
            # concentração" (52 chars) flips the area to MT for the rest of the
            # section -- 2017 day 1, in both the accessibility and AZUL
            # booklets, so it is the item's own words, not one edition's quirk.
            letters = [c for c in t if c.isalpha()]
            if letters and sum(c.isupper() for c in letters) / len(letters) < 0.6:
                continue
            area, lang = a, None
            break
        lr = LANG_RANGE.search(ln)
        if lr:
            lang_lo, lang_hi = int(lr.group(1)), int(lr.group(2))
            lang = "english" if lr.group(3).lower().startswith("ingl") else "spanish"
        else:
            lb = LANG_BLOCK.search(ln)
            if lb:
                lang = "english" if lb.group(1).lower().startswith("ingl") else "spanish"
                lang_lo = lang_hi = None   # no range stated; fall back below
        m = MARKER.match(ln)
        if m:
            if cur:
                out.append(cur)
            pos = int(m.group(1))
            # The foreign-language block is positions 1-5 of LC and nothing else.
            # The "(opção espanhol)" header stays in scope for the rest of the
            # area otherwise, which would label the 40 SHARED items as Spanish.
            # ITENS_PROVA agrees: TP_LINGUA is 0/1 only on positions 1-5 and
            # blank on 6-45.
            if area != "LC" or not lang:
                eff = None
            elif lang_lo is not None:
                eff = lang if lang_lo <= pos <= lang_hi else None
            else:
                # header gave no range: the block is the five positions that
                # open the area, whatever the year numbers them
                lc_seen = [g["position"] for g in out if g["area"] == "LC"] + [pos]
                eff = lang if pos <= min(lc_seen) + 4 else None
            cur = {"area": area, "lang": eff, "position": pos, "lines": []}
            continue
        if cur is not None:
            cur["lines"].append(ln)
        else:
            cover.append(ln)
    if cur:
        out.append(cur)
    return out, cover


def split_options(lines):
    """Return (stem, {letter: text}) or (None, None) if no clean A-E run exists."""
    cands = []
    for i, ln in enumerate(lines):
        if OPT_DOUBLE_MULTI.match(ln):
            for L in re.findall(r"([A-E])\1", ln):
                cands.append((i, L, "", "double"))
            continue
        m = OPT_DOUBLE_ALONE.match(ln)
        if m:
            cands.append((i, m.group(1), "", "double"))
            continue
        m = OPT_DOUBLE.match(ln)
        if m:
            cands.append((i, m.group(1), m.group(2), "double"))
            continue
        m = OPT_INLINE.match(ln)
        if m:
            cands.append((i, m.group(1), m.group(2), "inline"))
            continue
        m = OPT_ALONE.match(ln)
        if m:
            cands.append((i, m.group(1), "", "alone"))
    # Three option layouts occur. Each rule is deterministic; none guesses, and
    # an item matching none is reported rather than patched.
    #
    # (1) ASCENDING SUBSEQUENCE. The normal case, robust to spurious candidates.
    #     A wrapped option can start with a bare capital + space and register as
    #     a candidate: 2020 MT 84253 yields A,B,C,B,D,B,E where the extra Bs are
    #     continuation fragments ("- Xlog", "X"). The real options are the last
    #     strictly ascending A,B,C,D,E by line, so search for that, latest first.
    # (2) SET WINDOW. Long options are set in two columns, so extraction returns
    #     them out of alphabetical order -- 2019 MT 177 gives A,D,B,E,C. There is
    #     no ascending subsequence, so fall back to five CONSECUTIVE candidates
    #     whose letters form the set {A..E}; the printed letter is authoritative
    #     and the sequence is only layout.
    # (3) BARE-FIGURE OPTIONS (R5). When the printed options are figures with no
    #     text they are laid out several per line: 2020 MT 111491 extracts as
    #     "A D" / "B E" / "C". Detected by the marker letters plus their
    #     single-letter texts covering A-E, with no real text anywhere. Emits the
    #     five options with EMPTY text, which R5 requires and R5 also forbids
    #     filling in.
    # Prefer the doubled layout ONLY when the doubled candidates could actually
    # BE the option set. A single doubled hit used to discard every inline
    # candidate, and one line of Spanish was enough to lose a whole item:
    # 2015 LC 95 (item 67408) opens "EE UU ha propiciado que cada vez mas
    # estadounidenses...", where EE UU is the Spanish abbreviation for Estados
    # Unidos. OPT_DOUBLE read "EE" as a doubled marker for option E, the five
    # real inline options A-E were thrown away, and the item was reported
    # unsegmentable in AZUL, CINZA and ROSA alike -- which looked like a
    # property of the item because it followed the item across booklets.
    # A genuine doubled layout prints all five markers.
    dbl = [c for c in cands if c[3] == "double"]
    if len({c[1] for c in dbl}) == 5 or len(dbl) >= 5:
        cands = dbl
    best, bare = None, False
    for start in range(len(cands) - 1, -1, -1):
        if cands[start][1] != "A":
            continue
        pick, want = [cands[start]], 1
        for c in cands[start + 1:]:
            if want < 5 and c[1] == "ABCDE"[want]:
                pick.append(c); want += 1
        if want == 5:
            best = pick
            break
    if not best:
        for st in range(len(cands) - 4):
            run = cands[st:st + 5]
            if {r[1] for r in run} == set("ABCDE"):
                best = run
    if not best:
        tail = [c for c in cands if not c[2].strip() or re.fullmatch(r"[A-E]", c[2].strip())]
        letters = {c[1] for c in tail} | {c[2].strip() for c in tail if c[2].strip()}
        if letters == set("ABCDE") and tail:
            first = min(c[0] for c in tail)
            stem = "\n".join(lines[:first]).strip()
            return stem, {L: "NA" for L in "ABCDE"}
    if not best:
        return None, None
    def _hollow(txt, letter):
        t = (txt or "").strip()
        return t == "" or t == letter or t == letter * 2
    # Hollow markers are only a problem when the markers are CONTIGUOUS -- all
    # five adjacent, with every option's text following as one block. When the
    # markers are INTERLEAVED with their text (marker, text, marker, text ...)
    # the bounds logic below assigns each option correctly, and that is the
    # normal long-option layout: 2019 MT 177's "Descrição do gráfico:" options
    # are exactly that, and treating them as unsegmentable loses a real item
    # from a year that was already verified.
    ordered = sorted(best, key=lambda r: r[0])
    interleaved = any(
        any(l.strip() and not FURNITURE.match(l) for l in lines[a[0] + 1:b[0]])
        for a, b in zip(ordered, ordered[1:]))
    if all(_hollow(c[2], c[1]) for c in best) and not interleaved:
        # Hollow markers mean one of TWO things, and they must be told apart.
        #
        # (a) The printed options are bare figures -> R5, five NA options.
        # (b) The accessibility booklet sets long VERBAL options as five hollow
        #     marker lines followed by the five option texts as paragraphs:
        #        'B B '  'C C '  'D D '  'E E '
        #        'Fração de numerador 1 e denominador 46 mais ...'
        #        ... four more
        #     Emitting NA here DISCARDS the real options -- 240 words across
        #     2022 MT 47309, 86840 and 89637 -- and does so invisibly, because
        #     NA reads as a deliberate R5 ruling and passes every gate. That is
        #     strictly worse than the bug it replaced, which at least shipped a
        #     visibly wrong 'A'..'E'.
        #
        # The discriminator, measured: count non-furniture lines after the
        # marker block. Genuine bare-figure items have 0; the verbal-option
        # items have 16, 14 and 5.
        order = [c[1] for c in sorted(best, key=lambda r: r[0])]
        after = [l.strip() for l in lines[max(c[0] for c in best) + 1:]
                 if l.strip() and not FURNITURE.match(l)]
        stem = "\n".join(lines[:min(c[0] for c in best)]).strip()
        if len(after) >= len(order):
            # Paragraphs follow, so these are VERBAL options, not bare figures --
            # but they WRAP across lines, so "one line per option" is wrong:
            # 2022 MT 89637's option A spans two lines and a line-wise split
            # assigns its second half to option B. There is no reliable boundary
            # (the text is mathematical prose; even sentence-final "." is not
            # dependable), so this is REPORTED as unsegmentable rather than
            # guessed at.
            #
            # Emitting NA here instead would be worse than a visible failure:
            # NA reads as a deliberate R5 ruling, passes validate_items, passes
            # both gabarito checks, and silently drops the real options -- which
            # is exactly what it did for 2022 MT 47309, 86840 and 89637 (240
            # words) before this branch existed.
            return None, "verbal options below hollow markers, wrap unsegmentable"
        return stem, {L: "NA" for L in "ABCDE"}
    best = sorted(best, key=lambda r: r[0])   # line order, for text boundaries
    stem = "\n".join(lines[:best[0][0]]).strip()
    opts, bounds = {}, [r[0] for r in best] + [len(lines)]
    for k, (idx, letter, first, _kind) in enumerate(best):
        tail = lines[idx + 1:bounds[k + 1]]
        # the final option runs to the end of the item, which is where the next
        # area header or page number lands; drop that furniture from the tail
        if k == len(best) - 1:
            while tail and (not tail[-1].strip() or FURNITURE.match(tail[-1])):
                tail.pop()
        body = [x for x in ([first] + tail) if x.strip()]
        opts[letter] = "\n".join(body).strip()
    # ORPHAN FIGURE DESCRIPTION. INEP's accessibility booklet prints a
    # "Descrição d..." block for the STEM's figure after the last option, so it
    # lands in option E and describes the wrong thing: 2018 item 111434 ships
    # E = "11 por 11." + "Descrição da figura: Dois círculos concêntricos...".
    # 29 of 183 items in 2018 alone, and it is booklet structure rather than a
    # year quirk, so it hits every LEDOR year (2017-2022). No count-based gate
    # can see it.
    #
    # Discriminator: a block present in the LAST option and ABSENT from A-D
    # describes the stem. When all five options carry their own description
    # (2018 CN 43554, 111628) they are genuine per-option text and are left
    # alone, which this test excludes correctly.
    tail_letter = "E"
    tail = opts.get(tail_letter) or ""
    m = DESCRICAO.search(tail)
    if m and not any(DESCRICAO.search(opts.get(L) or "") for L in "ABCD"):
        opts[tail_letter] = tail[:m.start()].rstrip()
        moved = tail[m.start():].strip()
        stem = (stem + "\n" + moved).strip() if stem else moved

    # R5: are these real options, or a bare figure's interior?
    bodies = [(opts[L] or "").strip() for L in "ABCDE"]
    has_desc = any(DESCRICAO.search(b) for b in bodies)
    n_empty = sum(1 for b in bodies if not b or b == "NA")
    all_same = len({b for b in bodies}) == 1
    if not has_desc and (0 < n_empty < 5 or (all_same and bodies[0])):
        # Some options empty while others carry text, or all five identical:
        # printed options are figures and what came through is their interior or
        # a doubled-letter artefact. INEP's own Descrição marker overrides, since
        # a described option IS the option (2018 CN 43554, 111628).
        return stem, {L: "NA" for L in "ABCDE"}
    return stem, opts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--year", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", type=int, default=None,
                    help="expected item count; mismatch is reported, not fixed")
    a = ap.parse_args()

    segs, cover = segment(a.pdf)
    # Strip screen-reader-only lines: candidates in the response tables sat the
    # standard booklets and never read them (R7, ruled for 2023's "soletrar").
    SR = re.compile(r"(soletrar|leitor de tela|sintetizador de voz|dosvox|nvda)", re.I)
    cover_txt = "\n".join(l for l in cover if l.strip() and not SR.search(l)).strip()
    with open(a.out + ".cover.txt", "w", encoding="utf-8") as fh:
        fh.write(cover_txt)
    rows, bad = [], []
    for s in segs:
        if s["area"] is None:
            bad.append((None, s["position"], "no area header seen before this item"))
            continue
        stem, opts = split_options(s["lines"])
        if stem is None:
            why = opts if isinstance(opts, str) else "no clean A-E option run"
            bad.append((s["area"], s["position"], why))
            continue
        for letter in "ABCDE":
            rows.append({"year": a.year, "area": s["area"], "lang_block": s["lang"] or "",
                         "position": s["position"], "option_letter": letter,
                         "stem": stem, "option_text": opts[letter],
                         "source_file": os.path.basename(a.pdf)})
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["year", "area", "lang_block", "position",
                                "option_letter", "stem", "option_text", "source_file"])
        w.writeheader(); w.writerows(rows)

    n_items = len({(r["area"], r["lang_block"], r["position"]) for r in rows})
    per = {}
    for r in rows:
        per[r["area"]] = per.get(r["area"], set()) | {(r["lang_block"], r["position"])}
    print(f"  {os.path.basename(a.pdf)}")
    print(f"    parsed {n_items} items, {len(rows)} option rows -> {a.out}")
    print(f"    cover: {len(cover_txt)} chars -> {a.out}.cover.txt")
    for ar in sorted(per):
        print(f"      {ar}: {len(per[ar])} items")
    if bad:
        print(f"    {len(bad)} item(s) NOT parsed (reported, not guessed):")
        for ar, pos, why in bad[:10]:
            print(f"      {ar or '?'} position {pos}: {why}")
    if a.expect is not None and n_items != a.expect:
        print(f"    MISMATCH: expected {a.expect} items, parsed {n_items}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
