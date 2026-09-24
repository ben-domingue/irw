#!/usr/bin/env python3
"""Strip printed-page furniture that bleeds into the LAST field before a page break.

FOUND BY, and this matters: a cross-booklet agreement test. 2016 CH/CN were
extracted independently from AZUL and from BRANCA -- two physically different
booklets with separately subset fonts -- and compared by CO_ITEM. 873 of 890
fields agreed character-for-character (99.907% of characters, ZERO wrong
letters). Of the 17 that differed, 15 were spurious intra-word spaces and 2
were this: the running head and barcode of the FOLLOWING page appended to the
last option before the break, e.g.

    "...imigração de trabalhadores qualifi cados.
     CN - 1º dia | Caderno 1 - AZUL - Página 16
     *AZUL75SAB16*
     CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS
     Questões de 46 a 90"

Sweeping every year for the same signature found 112 affected items across 11
years -- 57 in 2013 and 32 in 2015, whose header format differs from the one
the parser already suppresses. The two booklets disagreed precisely BECAUSE the
furniture is booklet-specific, which is what made it visible; a single-booklet
check cannot see it at all.

WHY A POST-PASS AND NOT A PARSER CHANGE. Editing the pinned parser mid-flight
broke reproducibility once already (STATUS.md, 2026-09-14). This runs on the
joined tables -- the shipped artefact -- reports every removal for audit, and
can be re-run or reverted without re-parsing 46 booklets.

CONSERVATISM. Lines are removed ONLY from the tail of a field, ONLY while they
match one of the furniture patterns below, and the scan stops at the first line
that does not match. Nothing is ever removed from the middle of a field, so no
sentence can be truncated. Every removal is printed.

Usage:
  python3 26_strip_page_furniture.py --items-dir <dir> [--apply]
  # without --apply it is a dry run and writes nothing
"""
import argparse, csv, glob, os, re, sys

SCHEMA = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
          "item_text", "correct_response", "option_text", "resp", "item_text_translated",
          "option_text_translated", "instructions_translated", "section_prompt_translated",
          "language", "resp_raw"]

# Each pattern must match a WHOLE line (after strip) to be removable.
FURNITURE = [
    re.compile(r"^\*[A-Z0-9]+\*$"),                                  # *AZUL75SAB16*
    re.compile(r"^(CH|CN|LC|MT)\s*[-–]\s*\d\s*[º°o]\s*dia\s*\|.*$", re.I),
    re.compile(r"^\d\s*[º°o]\s*dia\s*\|\s*Caderno.*$", re.I),
    re.compile(r"^Caderno\s*\d+\s*[-–|]\s*[A-ZÇÃÕÉ]+\s*[-–|]\s*P[áa]gina\s*\d+$", re.I),
    re.compile(r"^\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}.*$"),        # 2025 render timestamps
    re.compile(r"^.*\|\s*\d\s*[ºO]\s*DIA\s*\|\s*CADERNO\s*\d+\s*\|\s*[A-ZÇÃÕÉ]+\s*\d*$"),
    re.compile(r"^(CI[ÊE]NCIAS DA NATUREZA|CI[ÊE]NCIAS HUMANAS|LINGUAGENS|"
               r"MATEM[ÁA]TICA)[A-ZÇÃÕÉ\s,]*TECNOLOGIAS$", re.I),
    re.compile(r"^Quest[õo]es\s+de\s+\d+\s+a\s+\d+$", re.I),
    re.compile(r"^P[áa]gina\s*\d+$", re.I),
]


# A line matching one of THESE cannot be item content at any position, so it is
# removed wherever it occurs -- needed because an item that spans a page break
# carries the furniture in the MIDDLE, with real text on both sides. This list
# is deliberately narrower than FURNITURE: it excludes the area names and
# "Questões de N a M", which are meaningful inside `instructions`.
# A barcode token can also be appended INLINE to real text
# ("Ministério da Educação *AZUL75SAB1*"), so the line must be kept and only the
# token removed. Requires >=5 alnum chars including a digit between asterisks,
# a shape no ENEM prose produces.
BARCODE_TOKEN = re.compile(r"\s*\*(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,}\*")

# The anti-fraud WATERMARK printed across the page background extracts as a run
# of "ENEM<year>" tokens (with occasional "ENEN<year>" typos in INEP's own
# artwork). Found in 2022's instructions on every table, one 2022 LC stem, and
# three 2025 option cells -- including 2025 MT 125905, whose option E consisted
# of NOTHING BUT the watermark while A-D were blank. Three or more repetitions
# is required so an item that legitimately mentions "ENEM 2025" once is safe.
WATERMARK = re.compile(r"(?:ENE[MN]\s*\d{4}\s*){3,}", re.I)

ANYWHERE = [
    re.compile(r"^\*[A-Za-z0-9]+\*$"),                               # *LE0175LA1*, *AZUL25dom1*
    re.compile(r"^(CH|CN|LC|MT)\s*[-\u2013]\s*\d\s*[\u00ba\u00b0o]\s*dia\s*\|.*$", re.I),
    re.compile(r"^\d\s*[\u00ba\u00b0o]\s*dia\s*\|.*$", re.I),   # orphan half of a split head
    # 2021 leaks the InDesign source filename and render timestamp, and puts
    # the page number BEFORE the area code so the head no longer starts with it.
    re.compile(r"^.*\.indb\s+\d+\s+\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}.*$", re.I),
    re.compile(r"^\s*\d{1,3}\s*(CH|CN|LC|MT)\s*[-\u2013]\s*\d\s*[\u00ba\u00b0o]\s*dia\s*\|.*$", re.I),
    re.compile(r"^LEDOR$"),
    re.compile(r"^\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}.*$"),
]
# The running head is sometimes SPLIT across two lines ("LC - " / "1o dia |
# Caderno 9 - LARANJA - Pagina 2"), so neither half matches on its own.
SPLIT_HEAD = (re.compile(r"^(CH|CN|LC|MT)\s*[-\u2013]\s*$", re.I),
              re.compile(r"^\d\s*[\u00ba\u00b0o]\s*dia\s*\|.*$", re.I))


def strip_anywhere(v, year=None):
    """Remove unambiguous furniture lines at ANY position in the field."""
    if not v:
        return v, []
    extra = [re.compile(r"^%s\s*(?:\*[A-Z0-9]+\*|LEDOR)?$" % year)] if year else []
    lines = v.split("\n")
    out, dropped, i = [], [], 0
    _ = None
    while i < len(lines):
        cur = lines[i].strip()
        if i + 1 < len(lines) and SPLIT_HEAD[0].match(cur) \
                and SPLIT_HEAD[1].match(lines[i + 1].strip()):
            dropped += [lines[i], lines[i + 1]]; i += 2; continue
        if cur and any(p.match(cur) for p in ANYWHERE + extra):
            dropped.append(lines[i]); i += 1; continue
        scrubbed = WATERMARK.sub("", BARCODE_TOKEN.sub("", lines[i]))
        if scrubbed != lines[i]:
            dropped.append(lines[i][len(scrubbed):] or "<inline barcode>")
        out.append(scrubbed); i += 1
    res = "\n".join(out)
    if dropped:                      # a removal can expose another; re-run
        res2, more = strip_anywhere(res, year)
        dropped += more
        res = res2
    return res, dropped


# Everything from one of these markers to the END of the field is a separate
# printed SECTION, not item content: the essay draft page (a numbered blank
# grid) and the essay instructions. They attach to whichever item precedes the
# section break. Found by AZUL-vs-ROSA disagreement in 2015 MT, where one
# booklet appended "RASCUNHO / DA REDAcAO / 1 / 2 / 3 ..." and the other did
# not. The whole line must equal the marker.
BLOCK_START = [
    re.compile(r"^RASCUNHO$", re.I),
    re.compile(r"^RASCUNHO\s+DA\s+REDA[ÇC][ÃA]O$", re.I),
    re.compile(r"^INSTRU[ÇC][ÕO]ES\s+PARA\s+A\s+REDA[ÇC][ÃA]O$", re.I),
]


def truncate_blocks(v):
    """Cut the field at the first line that starts a non-item printed section."""
    if not v:
        return v, 0
    lines = v.split("\n")
    for i, ln in enumerate(lines):
        if any(p.match(ln.strip()) for p in BLOCK_START):
            return "\n".join(lines[:i]), len(lines) - i
    return v, 0


def strip_tail(v, year=None):
    """Remove furniture lines from the END of a field only."""
    if not v:
        return v, 0
    # The bare-year footer is accepted ONLY as this booklet's own year. A loose
    # \d{4} rule would delete a legitimate option that is just a date, which is
    # a real ENEM answer shape ("A 1990 / B 1995 / C 2000").
    extra = [re.compile(r"^%s\s*(?:\*[A-Z0-9]+\*|LEDOR)?$" % year)] if year else []
    lines = v.split("\n")
    removed = 0
    while lines:
        last = lines[-1].strip()
        if last == "":
            lines.pop(); removed += 1; continue
        if any(p.match(last) for p in FURNITURE + extra):
            lines.pop(); removed += 1; continue
        # A furniture line can be WRAPPED: 2016 sets the next area's header as
        # "CIÊNCIAS DA NATUREZA E SUAS \n TECNOLOGIAS", so the trailing line is
        # the bare word TECNOLOGIAS and no single-line rule can see it. Join the
        # last 2-3 lines and re-test: the block is only removed when the JOINED
        # text matches a furniture pattern in full, so a real sentence whose
        # last word happens to be TECNOLOGIAS is never touched.
        hit = False
        for n in (4, 3, 2):
            if len(lines) < n:
                continue
            joined = re.sub(r"\s+", " ", " ".join(lines[-n:])).strip()
            if any(p.match(joined) for p in FURNITURE + extra):
                del lines[-n:]
                removed += n
                hit = True
                break
        if hit:
            continue
        break
    return "\n".join(lines), removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    n_files = n_fields = n_lines = 0
    for p in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        ym = re.search(r"enem_(\d{4})_", os.path.basename(p))
        year = ym.group(1) if ym else None
        hits = []
        for r in rows:
            for col in ("item_text", "option_text", "section_prompt", "instructions"):
                if col not in r or not r[col]:
                    continue
                mid, drop = strip_anywhere(r[col], year)
                mid, nb = truncate_blocks(mid)
                new, k = strip_tail(mid, year)
                k += len(drop) + nb
                if k:
                    hits.append((r["item"], col, k, r[col][len(new):][:80]))
                    r[col] = new
                    n_fields += 1; n_lines += k
        if hits:
            n_files += 1
            uniq = sorted({(i, c) for i, c, _, _ in hits})
            print(f"  {os.path.basename(p)}: {len(uniq)} item/field(s) cleaned")
            for i, c, k, what in hits[:3]:
                print(f"      item {i} [{c}] -{k} line(s): {what!r}")
        if a.apply and hits:
            with open(p, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA)
                w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in SCHEMA})
    verb = "cleaned" if a.apply else "WOULD clean (dry run)"
    print(f"  {verb}: {n_fields} field(s), {n_lines} furniture line(s), {n_files} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
