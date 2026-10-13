#!/usr/bin/env python3
"""Item text for yang_2026_epistemic_beliefs / _ai_literacy / _academic_dishonesty
(Mendeley 10.17632/252r6gdx48).

Cheap case: the deposit's "(1) Questionnaire.docx" lists every item code with its English stem;
data/yang_2026_ai_literacy_dishonesty.py stems() reads that table (BI4 -> BL4), so the item code
is the deposit's own column name. No anchors anywhere in the deposit, so option_text is blank on
all seven points. The administration language is not stated in the record (Chinese sample,
English questionnaire deposited), so language is left blank.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("yang_2026_ai_literacy_dishonesty")
INSTR = {"yang_2026_epistemic_beliefs": "Epistemic beliefs about AI tools/systems (Chiu et al., 2013)",
         "yang_2026_ai_literacy": "AI literacy (Ng et al., 2024)",
         "yang_2026_academic_dishonesty": "Academic dishonesty with AI tools/systems (Akbulut et al., 2008; Chan, 2025)"}


def main():
    en = mod.stems()
    for table, items in mod.TABLES.items():
        rows = [row(table, f"{table}_1", c, INSTR[table], "", r, en[c]) for c in items for r in range(1, 8)]
        write(table, rows)


if __name__ == "__main__":
    main()
