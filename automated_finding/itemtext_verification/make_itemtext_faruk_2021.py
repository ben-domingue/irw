#!/usr/bin/env python3
"""Item text for faruk_2021_phq9 / _gad7 / _soss (Mendeley 10.17632/ycv96d9pf3).

PHQ-9 and GAD-7: .sav variable labels are the stems (the PHQ labels carry a "PHQk " prefix on items
1-3, stripped). SOSS: no variable labels; stems from the deposited "English Questionnaire.docx", keyed by
the printed "SOSS-k:" number = column SOSS_k. Anchors are taken from the questionnaire as administered
(PHQ/GAD: Not at all / Several days / More than half days / All the days; SOSS: five agreement anchors).
English questionnaire deposited; language left blank.
"""
import re

import docx

from _itemtext_writer_c import load_script, row, write

mod = load_script("faruk_2021_dental_students")
FREQ = {0: "Not at all", 1: "Several days", 2: "More than half days", 3: "All the days"}
AGREE = {1: "Strongly disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly Agree"}
PROMPT = "Within previous 2 weeks how you have faced the underlying condition?"


def main():
    labels, _ = mod.labels()
    doc = docx.Document(mod.mendeley_fetch("ycv96d9pf3", "English Questionnaire.docx", mod.RAW_DIR))
    text = "\n".join(p.text for p in doc.paragraphs)
    soss = {int(k): " ".join(v.split()) for k, v in re.findall(r"SOSS-(\d+):\s*(.+)", text)}
    assert len(soss) == 16
    for table, items, instr in [("faruk_2021_phq9", mod.PHQ, "Patient Health Questionnaire (PHQ-9)"),
                                ("faruk_2021_gad7", mod.GAD, "Generalized Anxiety Disorder scale (GAD-7)")]:
        rows = []
        for c in items:
            stem = re.sub(r"^PHQ\d+\s+", "", labels[c]).strip()
            rows += [row(table, f"{table}_1", c, instr, "", r, stem, option_text=FREQ[r], section_prompt=PROMPT) for r in FREQ]
        write(table, rows)
    rows = [row("faruk_2021_soss", "faruk_2021_soss_1", f"SOSS_{k}", "Stigma of Suicide Scale (SOSS-16)", "", r, soss[k], option_text=AGREE[r])
            for k in range(1, 17) for r in AGREE]
    write("faruk_2021_soss", rows)


if __name__ == "__main__":
    main()
