#!/usr/bin/env python3
"""Parse an ENEM DOSVOX accessibility booklet (plain text) into the same CSV
that 12_parse_booklet_pdf.py emits, so 13_join.py and 14_fill_gaps.py work
unchanged.

The DOSVOX path for 2024 and 2025. EXTRACTION_RULES.md R1.1 prefers the
accessibility edition because INEP wrote verbal descriptions of figures,
graphs and tables into it; those arrive here as "Descrição d..." lines and are
kept as item text, terminator line "(Fim da descrição)" included.

OUTPUT CONTRACT, identical to 12_parse_booklet_pdf.v2.py (md5
d345acc79464ea31c90f534bada963ae):
    <out>            year, area, lang_block, position, option_letter,
                     stem, option_text, source_file
    <out>.cover.txt  the booklet cover, screen-reader-only lines stripped,
                     which 13_join.py reads for R7 `instructions`
Knows nothing about CO_ITEM: that is 13_join.py's job and R0's rule.

HOW 2024/2025 DIFFER FROM 2023, which shipped first (#1848):

1. ONE FILE PER DAY, TWO AREAS. 2023 shipped four files, one per area, and its
   parser took the area from the FILENAME. 2024/2025 ship
   "2024_Dia_1_P1_LC_CH_..." carrying LC 1-45 and CH 46-90 in one file, so the
   area has to be read from the printed section headers mid-file, the way the
   PDF parser does it. The filename is used only as a cross-check.

2. TWO OPTION PUNCTUATIONS. 2024 prints "a. texto"; 2025 prints "a) texto".
   Both are accepted, as is a letter alone on its own line.

3. MARKER CASE AND TRAILING WHITESPACE. 2024 prints "QUESTÃO 91"; 2025 prints
   "Questão 91". 2024 day 1 prints "QUESTÃO 29 \t" with a trailing TAB, which
   a `[ ]*$` anchor misses -- and the failure is silent, because the item's
   text is absorbed into its predecessor and only the count differs (trap 9).

4. NO LANGUAGE-BLOCK RESET IN 2025. 2024 reprints
   "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS / Questões de 6 a 45" after the
   Spanish block; 2025 prints nothing at all, so "(opção espanhol)" stays in
   scope for the rest of LC and would label all 40 SHARED items Spanish, with
   no count anywhere revealing it (trap 5). Handled the same way the PDF
   parser handles it: the foreign-language block is LC positions 1-5 and
   nothing else, which is what ITENS_PROVA's TP_LINGUA says too.

5. A GENUINE SHARED PASSAGE EXISTS IN 2025 LC. "Texto para as Questões de
   6 a 10" introduces a 45-line numbered crônica that sits between the Spanish
   block's last option and the "Questão 6" marker. Marker-based segmentation
   would swallow it into the PRECEDING item's last option and leave items 6-10
   with no stimulus at all -- again with every count correct. R7 reserves
   `section_prompt` for exactly this and says to verify it per year rather
   than assume 2023's "no shared passages" answer.

   This parser does not decide the question. It
     - never lets orphan text leak into the previous item's last option,
     - attaches the passage to the item_text of every item in its printed
       range, so no printed text is lost,
     - records it in <out>.shared_passages.csv, and
     - REPORTS it, because whether it belongs in section_prompt instead is a
       ruling for the user, not a judgement for this script (R11).

TRAPS INHERITED FROM 12_parse_booklet_pdf.v2.py, all of which pass a
count-based check, so none of them is theoretical:

  - Option letters are AUTHORITATIVE and their order is only layout, so the
    option block is found as the last ASCENDING A-E subsequence (not a window,
    not the first ^[A-E] match), with a set-window fallback for options laid
    out in columns and a bare-figure fallback for R5.
  - A wrapped option can begin with a bare capital and register as a spurious
    candidate, which is why the subsequence rule exists.
  - Section headers are CAPITALISED and item prose is not: without that guard
    a CH stem line containing "matemática" flips the tracked area to MT for
    the rest of the section (trap 8).

Nothing is guessed. An item whose options cannot be resolved is reported.

Usage:
  python3 19_parse_dosvox.py <dosvox.txt> --year 2024 --out items.csv [--expect 95]
"""
import argparse, csv, os, re, sys, unicodedata

AREA_HEADERS = [
    (re.compile(r"LINGUAGENS,?\s+C[ÓO]DIGOS", re.I), "LC"),
    (re.compile(r"CI[ÊE]NCIAS\s+HUMANAS", re.I), "CH"),
    (re.compile(r"CI[ÊE]NCIAS\s+DA\s+NATUREZA", re.I), "CN"),
    (re.compile(r"MATEM[ÁA]TICA", re.I), "MT"),
]
LANG_BLOCK = re.compile(r"op[çc][ãa]o\s+(ingl[êe]s|espanhol)", re.I)
# "QUESTÃO 29 \t" occurs (2024 day 1): \s covers the tab, [ ] would not.
MARKER = re.compile(r"^\s*Quest[ãa]o\s+(\d{1,3})\s*[.;:]?\s*$", re.I)
# "a. texto" (2024) and "a) texto" (2025). The delimiter is REQUIRED: a bare
# "a " would match Portuguese prose lines beginning with the preposition "a",
# which is the false-positive the PDF parser has to work around and DOSVOX
# does not.
OPT_INLINE = re.compile(r"^\s*([A-Ea-e])\s*[.)]\s+(\S.*)$")
OPT_ALONE = re.compile(r"^\s*([A-Ea-e])\s*[.)]\s*$")
# Lines that are booklet structure, never item content. Deliberately NOT
# "(Fim da ...": "(Fim da descrição)" sits on its own line 20+ times per day-2
# file and IS item content -- it closes an INEP figure description.
RANGE = re.compile(r"^\s*Quest[õo]es\s+de\s+\d+\s+a\s+\d+", re.I)
SHARED_HDR = re.compile(
    r"^\s*Textos?\s+para\s+as\s+Quest[õo]es\s+de\s+(\d+)\s+a\s+(\d+)", re.I)
REDACAO = re.compile(r"^\s*(INSTRU[ÇC][ÕO]ES\s+PARA\s+A\s+REDA[ÇC][ÃA]O"
                     r"|PROPOSTA\s+DE\s+REDA[ÇC][ÃA]O)", re.I)
END_PROVA = re.compile(r"^\s*\(Fim d(a|as)\s+prova", re.I)
PROVA_DE = re.compile(r"^\s*PROVA DE\s+(.+)$")
# Screen-reader-only cover lines: candidates in the response tables sat the
# standard booklets and never read these (R7, ruled 2026-09-11 for 2023's
# "soletrar" line). Same expression as 12_parse_booklet_pdf.py, plus the
# standalone edition label -- 2024 prints "DOSVOX" on a line of its own and
# 2025 prints "Ledor", which is the same class of line.
SCREEN_READER = re.compile(r"(soletrar|leitor de tela|sintetizador de voz|dosvox|nvda)", re.I)
EDITION_LABEL = re.compile(r"^\s*(DOSVOX|Ledor)\s*$", re.I)
# printed position ranges by area, as the booklets number them
PRINTED = {"LC": (1, 45), "CH": (46, 90), "CN": (91, 135), "MT": (136, 180)}
AREA_NAME = {
    "LC": "Linguagens, Códigos e suas Tecnologias",
    "CH": "Ciências Humanas e suas Tecnologias",
    "CN": "Ciências da Natureza e suas Tecnologias",
    "MT": "Matemática e suas Tecnologias",
}


def read_lines(path):
    """The four DOSVOX files are cp1252 with CRLF, not UTF-8."""
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw.decode("cp1252").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def is_area_header(ln):
    t = ln.strip()
    if len(t) >= 60:
        return None
    for rx, a in AREA_HEADERS:
        if not rx.search(ln):
            continue
        # A section header is SET IN CAPITALS; item prose is not (trap 8).
        letters = [c for c in t if c.isalpha()]
        if letters and sum(c.isupper() for c in letters) / len(letters) < 0.6:
            return None
        return a
    return None


def structural(ln):
    """True for booklet furniture that must not be swallowed into an item."""
    return bool(is_area_header(ln) or RANGE.match(ln) or SHARED_HDR.match(ln)
                or REDACAO.match(ln) or END_PROVA.match(ln) or PROVA_DE.match(ln))


def segment(lines):
    """Walk the lines once, tracking area and language block, cutting at markers.

    Returns (segments, cover). cover is everything before the first marker,
    which is what R7 calls `instructions`.
    """
    area, lang, cur, out, cover = None, None, None, [], []
    for ln in lines:
        a = is_area_header(ln)
        if a:
            area, lang = a, None
        lb = LANG_BLOCK.search(ln)
        if lb:
            lang = "english" if lb.group(1).lower().startswith("ingl") else "spanish"
        m = MARKER.match(ln)
        if m:
            if cur:
                out.append(cur)
            pos = int(m.group(1))
            # The foreign-language block is LC positions 1-5 and nothing else.
            # 2025 never reprints a reset header, so "(opção espanhol)" would
            # otherwise stay in scope and label the 40 SHARED items Spanish
            # (trap 5). ITENS_PROVA agrees: TP_LINGUA is 0/1 only on 1-5.
            eff = lang if (area == "LC" and pos <= 5) else None
            cur = {"area": area, "lang": eff, "position": pos, "lines": []}
            continue
        if cur is not None:
            cur["lines"].append(ln)
        else:
            cover.append(ln)
    if cur:
        out.append(cur)
    return out, cover


def pick_options(cands):
    """Choose the printed option block from the candidate lines.

    Lifted from 12_parse_booklet_pdf.v2.py's split_options, whose three rules
    are each deterministic:
      (1) the last strictly ASCENDING A,B,C,D,E subsequence -- the normal case,
          robust to a wrapped option that begins with a bare capital;
      (2) five CONSECUTIVE candidates whose letters form the SET {A..E}, for
          options set in columns and extracted out of order (the printed letter
          is authoritative; the order is layout);
      (3) bare-figure options (R5), detected as letter markers whose only text
          is another letter, which yield five options with EMPTY text.
    Returns (picked, bare_figure) or (None, False).
    """
    for start in range(len(cands) - 1, -1, -1):
        if cands[start][1] != "A":
            continue
        pick, want = [cands[start]], 1
        for c in cands[start + 1:]:
            if want < 5 and c[1] == "ABCDE"[want]:
                pick.append(c)
                want += 1
        if want == 5:
            return pick, False
    for st in range(len(cands) - 4):
        run = cands[st:st + 5]
        if {r[1] for r in run} == set("ABCDE"):
            return run, False
    tail = [c for c in cands
            if not c[2].strip() or re.fullmatch(r"[A-Ea-e]", c[2].strip())]
    letters = {c[1] for c in tail} | {c[2].strip().upper() for c in tail if c[2].strip()}
    if tail and letters == set("ABCDE"):
        return tail, True
    return None, False


def split_item(lines):
    """Return (stem, {letter: text}, orphan_lines) for one item block.

    orphan_lines is everything after the option block that is not this item's
    text: the booklet furniture between two items, and -- the reason this is
    returned rather than silently dropped -- any SHARED PASSAGE printed for the
    items that follow. Letting it run into the last option is what a naive
    "last option runs to the end of the block" rule does, and it costs items
    6-10 of 2025 LC their entire stimulus while every count stays correct.
    """
    cands = []
    for i, ln in enumerate(lines):
        m = OPT_INLINE.match(ln)
        if m:
            cands.append((i, m.group(1).upper(), m.group(2)))
            continue
        m = OPT_ALONE.match(ln)
        if m:
            cands.append((i, m.group(1).upper(), ""))
    best, bare = pick_options(cands)
    if not best:
        return None, None, []
    best = sorted(best, key=lambda r: r[0])       # line order, for boundaries
    stem_lines = [l for l in lines[:best[0][0]] if l.strip() and not structural(l)]
    stem = "\n".join(x.strip() for x in stem_lines).strip()
    if bare:
        # R5: the printed options are figures with no text. Five options, no
        # text, and never a generated label.
        return stem, {L: "" for L in "ABCDE"}, []

    # The last option ends at the first structural line after it; whatever
    # follows belongs to no item and is handed back as orphan text.
    last = best[-1][0]
    end = len(lines)
    for j in range(last + 1, len(lines)):
        if structural(lines[j]):
            end = j
            break
    opts, bounds = {}, [r[0] for r in best[1:]] + [end]
    for k, (idx, letter, first) in enumerate(best):
        tail = lines[idx + 1:bounds[k]]
        body = [x.strip() for x in ([first] + tail) if x.strip()]
        opts[letter] = "\n".join(body).strip()
    orphan = lines[end:]
    return stem, opts, orphan


def norm(x):
    return "".join(c for c in unicodedata.normalize("NFKD", x.upper())
                   if not unicodedata.combining(c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("txt")
    ap.add_argument("--year", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", type=int, default=None,
                    help="expected item count; mismatch is reported, not fixed")
    a = ap.parse_args()

    lines = read_lines(a.txt)
    segs, cover = segment(lines)

    rows, bad, shared, orphans, range_bad = [], [], [], [], []
    # pass 1: options and stems, collecting the orphan text between items
    for s in segs:
        if s["area"] is None:
            bad.append((None, s["position"], "no area header seen before this item"))
            continue
        lo, hi = PRINTED[s["area"]]
        if not (lo <= s["position"] <= hi):
            range_bad.append((s["area"], s["position"]))
        stem, opts, orphan = split_item(s["lines"])
        if stem is None:
            bad.append((s["area"], s["position"], "no clean A-E option run"))
            continue
        s["stem"], s["opts"] = stem, opts
        for ln in orphan:
            m = SHARED_HDR.match(ln)
            if m:
                shared.append({"area": s["area"], "after_position": s["position"],
                               "lo": int(m.group(1)), "hi": int(m.group(2)),
                               "header": ln.strip(), "lines": []})
                continue
            if not ln.strip() or structural(ln):
                continue
            if shared and shared[-1]["after_position"] == s["position"]:
                shared[-1]["lines"].append(ln.strip())
            else:
                orphans.append({"area": s["area"], "after_position": s["position"],
                                "text": ln.strip()[:120]})

    # pass 2: attach each shared passage to every item in its printed range.
    # No printed text is lost. Whether it belongs in section_prompt instead is
    # reported, not decided here (R7/R11).
    for sp in shared:
        sp["text"] = "\n".join(sp["lines"]).strip()
        sp["attached"] = []
        for s in segs:
            if s["area"] != sp["area"] or "stem" not in s:
                continue
            if sp["lo"] <= s["position"] <= sp["hi"] and s["position"] > sp["after_position"]:
                s["stem"] = (sp["header"] + "\n" + sp["text"] + "\n" + s["stem"]).strip() \
                    if sp["text"] else s["stem"]
                sp["attached"].append(s["position"])

    for s in segs:
        if "stem" not in s:
            continue
        for letter in "ABCDE":
            rows.append({"year": a.year, "area": s["area"], "lang_block": s["lang"] or "",
                         "position": s["position"], "option_letter": letter,
                         "stem": s["stem"], "option_text": s["opts"][letter],
                         "source_file": os.path.basename(a.txt)})

    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["year", "area", "lang_block", "position",
                                "option_letter", "stem", "option_text", "source_file"])
        w.writeheader()
        w.writerows(rows)

    cover_txt = "\n".join(l.strip() for l in cover
                          if l.strip() and not SCREEN_READER.search(l)
                          and not EDITION_LABEL.match(l)).strip()
    with open(a.out + ".cover.txt", "w", encoding="utf-8") as fh:
        fh.write(cover_txt)

    if shared:
        with open(a.out + ".shared_passages.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, ["area", "lo", "hi", "header", "attached", "text"])
            w.writeheader()
            for sp in shared:
                w.writerow({"area": sp["area"], "lo": sp["lo"], "hi": sp["hi"],
                            "header": sp["header"],
                            "attached": " ".join(str(p) for p in sp["attached"]),
                            "text": sp["text"]})

    n_items = len({(r["area"], r["lang_block"], r["position"]) for r in rows})
    per = {}
    for r in rows:
        per[r["area"]] = per.get(r["area"], set()) | {(r["lang_block"], r["position"])}
    print(f"  {os.path.basename(a.txt)}")
    print(f"    parsed {n_items} items, {len(rows)} option rows -> {a.out}")
    for ar in sorted(per):
        langs = sorted({l for l, _ in per[ar] if l})
        extra = f", lang blocks {langs}" if langs else ""
        print(f"      {ar}: {len(per[ar])} items{extra}")
    print(f"    cover: {len(cover_txt)} chars -> {a.out}.cover.txt")
    # the booklet names the areas it carries on its cover; confirm we found them
    printed = [PROVA_DE.match(l).group(1).strip() for l in cover if PROVA_DE.match(l)]
    for ar in sorted(per):
        if printed and not any(norm(AREA_NAME[ar]) in norm(p) for p in printed):
            print(f"    WARNING: parsed area {ar} is not named on the cover {printed}")
    if range_bad:
        print(f"    {len(range_bad)} item(s) OUTSIDE the printed range for their area "
              f"(area header tracking is wrong): {range_bad[:10]}")
    if bad:
        print(f"    {len(bad)} item(s) NOT parsed (reported, not guessed):")
        for ar, pos, why in bad[:10]:
            print(f"      {ar or '?'} position {pos}: {why}")
    for sp in shared:
        print(f"    SHARED PASSAGE (R7 -- needs a ruling, see --help): {sp['area']} "
              f"{sp['header']!r}, {len(sp['text'])} chars, attached to positions "
              f"{sp['attached']}")
    if orphans:
        print(f"    {len(orphans)} orphan line(s) belonging to no item:")
        for o in orphans[:8]:
            print(f"      {o['area']} after position {o['after_position']}: {o['text']!r}")
    empty = [(r["area"], r["position"]) for r in rows if not r["option_text"].strip()]
    if empty:
        print(f"    {len(set(empty))} item(s) with at least one empty option "
              f"(R5 candidates): {sorted(set(empty))[:8]}")
    if a.expect is not None and n_items != a.expect:
        print(f"    MISMATCH: expected {a.expect} items, parsed {n_items}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
