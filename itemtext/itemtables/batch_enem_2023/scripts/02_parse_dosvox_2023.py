#!/usr/bin/env python3
"""
ENEM 2023 item text -- parse the DOSVOX accessibility-booklet plain text.

Primary source for 181 of the 185 main-application items. The other 4, plus one
figure-description patch, come from 01_pdf_sourced_2023.py -- see PROVENANCE.md.

INPUT  4 files, one per area, under
       extracted_2023/microdados_enem_2023/PROVAS E GABARITOS/
       ENEM_2023_P1_CAD_{09,11}_DIA_{1,2}_LARANJA_LEITOR_TELA_DOSVOX_{CH,LC,CN,MT}.txt
       Windows-1252, CRLF.

OUTPUT parsed_dosvox_items_2023.csv       area, position, tp_lingua, item_text,
                                          option_letter, option_text
       parsed_dosvox_instrument_2023.csv  area, instrument, instructions

STRUCTURE (verified against all 4 files, 185 questions):
  - a header block, ending at the first "Questões de N a M" line
  - then "QUESTÃO N" markers; N is the GLOBAL position printed in the booklet
    (LC 1-45, CH 46-90, CN 91-135, MT 136-180), which is ITENS_PROVA.CO_POSICAO
  - within a block: stem lines, then exactly 5 options "a. " .. "e. ",
    each on a SINGLE line (checked: no option wraps)
  - LC holds 50 questions for 45 positions: positions 1-5 appear twice, under
    explicit "Questões de 1 a 5 (opção inglês)" / "(opção espanhol)" headers.
    inglês -> TP_LINGUA 0, espanhol -> TP_LINGUA 1, everything else blank.
  - trailing non-option lines (end-of-prova markers, area/language headers, and
    the REDAÇÃO essay prompt after LC Q45) are NOT item content and are dropped.
    The essay is not an item in the IRW response tables.

section_id / section_prompt are deliberately absent: no ENEM 2023 item shares a
passage with another. Verified four ways -- no shared-passage markers, no question
lacking its own stem, no adjacent stems >45% similar, no long sentence appearing in
two stems. Each item's stimulus belongs in item_text.
"""
import csv, glob, os, re, sys, unicodedata

BOOK = os.path.expanduser(
    "~/enem/extracted_2023/microdados_enem_2023/PROVAS E GABARITOS")
OUT = os.path.dirname(os.path.abspath(__file__))

Q_RE    = re.compile(r"^QUESTÃO\s+(\d+)\s*$")
OPT_RE  = re.compile(r"^([a-e])\.\s+(.*)$")
RANGE_RE = re.compile(r"^Questões de \d+ a \d+")
LANG_RE = re.compile(r"^Questões de 1 a 5 \(opção (inglês|espanhol)\)")
PROVA_RE = re.compile(r"^PROVA DE (.+)$")
# The booklet prints the area name in all caps; .title() mangles Portuguese
# ("Ciências Da Natureza E Suas Tecnologias"), so use INEP's official names.
AREA_NAME = {
    "LC": "Linguagens, Códigos e suas Tecnologias",
    "CH": "Ciências Humanas e suas Tecnologias",
    "CN": "Ciências da Natureza e suas Tecnologias",
    "MT": "Matemática e suas Tecnologias",
}
# Lines that are structural, never item content.
DROP_RE = re.compile(r"^(\(Fim (da|das) |INSTRUÇÕES PARA A REDAÇÃO|PROPOSTA DE REDAÇÃO"
                     r"|TEXTO \d+$|PROVA DE )")

LANG = {"inglês": "0", "espanhol": "1"}


def read_booklet(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw.decode("cp1252").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def parse(path):
    area = re.search(r"DOSVOX_([A-Z]{2})\.txt$", path).group(1)
    lines = read_booklet(path)

    # ---- header block: everything before the first "Questões de N a M" ------
    first_range = next(i for i, l in enumerate(lines) if RANGE_RE.match(l))
    header = [l.strip() for l in lines[:first_range] if l.strip()]
    if area not in AREA_NAME:
        raise SystemExit(f"unknown area {area}")
    instrument = f"ENEM 2023 — Prova de {AREA_NAME[area]}"
    # Confirm the booklet really is the area its filename claims.
    printed = next((PROVA_RE.match(l).group(1) for l in header if PROVA_RE.match(l)), "")
    if printed:
        norm = lambda x: "".join(c for c in unicodedata.normalize("NFKD", x.upper())
                                 if not unicodedata.combining(c))
        if norm(AREA_NAME[area]) not in norm(printed):
            raise SystemExit(f"{area}: filename says {AREA_NAME[area]!r} "
                             f"but booklet prints {printed!r}")
    # Instructions: from the "ATENÇÃO:" line to the end of the header.
    try:
        start = next(i for i, l in enumerate(header) if l.startswith("ATENÇÃO"))
    except StopIteration:
        start = 0
    instructions = "\n".join(header[start:])

    # ---- questions ----------------------------------------------------------
    qidx = [i for i, l in enumerate(lines) if Q_RE.match(l)]
    if not qidx:
        raise SystemExit(f"{path}: no QUESTÃO markers")

    # Walk the whole file once to know which language section each question is in.
    lang_at = {}
    cur = ""
    for i, l in enumerate(lines):
        m = LANG_RE.match(l.strip())
        if m:
            cur = LANG[m.group(1)]
        elif RANGE_RE.match(l.strip()) and not m:
            # a plain "Questões de 6 a 45" ends the foreign-language block
            cur = ""
        if Q_RE.match(l):
            lang_at[i] = cur

    rows = []
    for k, i in enumerate(qidx):
        pos = Q_RE.match(lines[i]).group(1)
        end = qidx[k + 1] if k + 1 < len(qidx) else len(lines)
        blk = lines[i + 1:end]

        opt_at = [j for j, l in enumerate(blk) if OPT_RE.match(l)]
        if len(opt_at) != 5:
            raise SystemExit(f"{area} Q{pos}: found {len(opt_at)} options, expected 5")

        stem_lines = [l.strip() for l in blk[:opt_at[0]]
                      if l.strip() and not DROP_RE.match(l.strip())
                      and not RANGE_RE.match(l.strip())]
        item_text = "\n".join(stem_lines)

        opts = []
        for j in opt_at:
            m = OPT_RE.match(blk[j])
            opts.append((m.group(1).upper(), m.group(2).strip()))
        letters = [a for a, _ in opts]
        if letters != list("ABCDE"):
            raise SystemExit(f"{area} Q{pos}: option letters {letters}")

        for letter, text in opts:
            rows.append(dict(area=area, position=pos, tp_lingua=lang_at[i],
                             item_text=item_text,
                             option_letter=letter, option_text=text))
    return area, instrument, instructions, rows


def main():
    files = sorted(glob.glob(os.path.join(BOOK, "*DOSVOX*.txt")))
    if len(files) != 4:
        raise SystemExit(f"expected 4 DOSVOX files, found {len(files)}")

    all_rows, instr_rows = [], []
    for f in files:
        area, instrument, instructions, rows = parse(f)
        nq = len({(r["area"], r["position"], r["tp_lingua"]) for r in rows})
        print(f"  {area}: {nq} questions, {len(rows)} option rows")
        all_rows += rows
        instr_rows.append(dict(area=area, instrument=instrument,
                               instructions=instructions))

    p1 = os.path.join(OUT, "parsed_dosvox_items_2023.csv")
    with open(p1, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["area", "position", "tp_lingua", "item_text",
                                "option_letter", "option_text"])
        w.writeheader(); w.writerows(all_rows)

    p2 = os.path.join(OUT, "parsed_dosvox_instrument_2023.csv")
    with open(p2, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["area", "instrument", "instructions"])
        w.writeheader(); w.writerows(instr_rows)

    nq = len({(r["area"], r["position"], r["tp_lingua"]) for r in all_rows})
    print(f"\nwrote {p1}  ({nq} questions, {len(all_rows)} option rows)")
    print(f"wrote {p2}  ({len(instr_rows)} areas)")


if __name__ == "__main__":
    main()
