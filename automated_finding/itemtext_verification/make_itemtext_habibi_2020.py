#!/usr/bin/env python3
"""Item text for habibi_2020_tsc / _te (Mendeley 10.17632/6jmv43nffk). The deposited instrument docx
prints each block in Indonesian and then in English, five statements under "Konsep Diri Guru (TSC, 5)"
/ "Teacher Self-Concept (TSC, 5)" and "Khasiat Guru (TE, 5)" / "Teacher Efficacy (TE, 5)"; the k-th
statement is column TSCk / TEk (positional). Anchors are not printed (1-5 in the data), so option_text
is blank. Indonesian administration; English is the authors' own.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("habibi_2020_teacher_burnout")
HEADS = {"tsc": ("Konsep Diri Guru (TSC, 5)", "Teacher Self-Concept (TSC, 5)", "Teacher self-concept (TSC), 5 items"),
         "te": ("Khasiat Guru (TE, 5)", "Teacher Efficacy (TE, 5)", "Teacher efficacy (TE), 5 items")}


def block(lines, head):
    i = [n for n, l in enumerate(lines) if l.strip() == head][0]
    return [" ".join(l.split()) for l in lines[i + 1:i + 6]]


def main():
    import docx
    doc = docx.Document(mod.mendeley_fetch("6jmv43nffk", "1. Instrument in English and Indonesian.docx", mod.RAW_DIR))
    lines = [p.text for p in doc.paragraphs if p.text.strip()]
    for k, (h_id, h_en, instr) in HEADS.items():
        ind, en = block(lines, h_id), block(lines, h_en)
        table = f"habibi_2020_{k}"
        rows = [row(table, f"{table}_1", f"{k.upper()}{i}", instr, "Indonesian", r, ind[i - 1], option_text="", item_text_tr=en[i - 1])
                for i in range(1, 6) for r in range(1, 6)]
        write(table, rows)


if __name__ == "__main__":
    main()
