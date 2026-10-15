#!/usr/bin/env python3
"""Item text for ma_2026_psec / _tpi / _towb (Harvard Dataverse DVN/KXNKRI).

Chinese stems (as administered) from the deposited Questionnaire.pdf, numbered 1-30 in block order
(1-5 PSEC, 6-18 TPI, 19-30 TOWB; attention checks are unnumbered); English from Codebook.docx, keyed by
variable name. Anchors: the questionnaire's 1-7 legend, English from the codebook.
"""
import re
import subprocess

import docx

from _itemtext_writer_c import load_script, row, write

mod = load_script("ma_2026_teacher_wellbeing")
ZH = {1: "非常不同意", 2: "不同意", 3: "有点不同意", 4: "一般", 5: "有点同意", 6: "同意", 7: "非常同意"}
EN = {1: "Strongly Disagree", 2: "Disagree", 3: "Somewhat Disagree", 4: "Neutral", 5: "Somewhat Agree", 6: "Agree", 7: "Strongly Agree"}
INSTR = {"psec": "Perceived social-emotional competence (PSEC), 5 items", "tpi": "Teacher professional identity (TPI), 13 items",
         "towb": "Teacher occupational well-being (TOWB), 12 items"}


def chinese_items():
    pdf = mod.dv_fetch("10.7910/DVN/KXNKRI", "Questionnaire.pdf", mod.RAW_DIR)
    txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    txt = txt[txt.index("第三部分"):]
    txt = re.sub(r"\n\s*\d+\s*\n", "\n", txt)  # page numbers
    out = {}
    for m in re.finditer(r"(?<!\d)(\d{1,2})\.\s*(.+?)\s*\[\s*单\s*选题\s*\]", txt, flags=re.S):
        k, stem = int(m.group(1)), " ".join(m.group(2).split())
        stem = re.sub(r"[○\s]*\d?\s*$", "", stem)
        if 1 <= k <= 30 and k not in out:
            out[k] = stem.replace(" ", "")
    assert sorted(out) == list(range(1, 31)), sorted(out)
    return out


def english_items():
    doc = docx.Document(mod.dv_fetch("10.7910/DVN/KXNKRI", "Codebook.docx", mod.RAW_DIR))
    out = {}
    for t in doc.tables:
        for r in t.rows:
            cells = [c.text.strip() for c in r.cells]
            if re.fullmatch(r"(PSEC|TPI|TOWB)\d+", cells[0]):
                out[cells[0]] = " ".join(cells[1].split())
    return out


def main():
    zh, en = chinese_items(), english_items()
    codes = mod.BLOCKS["psec"] + mod.BLOCKS["tpi"] + mod.BLOCKS["towb"]
    assert len(codes) == 30 and set(codes) == set(en)
    for k, v in mod.BLOCKS.items():
        table = f"ma_2026_{k}"
        rows = []
        for c in v:
            n = codes.index(c) + 1
            for r in range(1, 8):
                rows.append(row(table, f"{table}_1", c, INSTR[k], "Chinese", r, zh[n], option_text=ZH[r],
                                item_text_tr=en[c], option_text_tr=EN[r]))
        write(table, rows)


if __name__ == "__main__":
    main()
