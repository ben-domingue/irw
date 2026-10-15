#!/usr/bin/env python3
"""Item text for le_2024_digicas_hps (Mendeley 10.17632/z9w44pc4dp). Stems from the deposited
"Information support file.docx", S3 appendix table (the 37-item DigiCAS-HPS questionnaire; "#" | item | (1)..(5)):
printed number k = column Qk (the docx's last table, the 16-item CFA subset, cites these as Q2, Q3 ...). Anchors from the printed instruction (Very unlikely .. Very likely).
The deposit prints the instrument in English and does not state the administration language
(Vietnamese students) -> language left blank.
"""
import re

import docx

from _itemtext_writer_c import load_script, row, write

mod = load_script("le_2024_digicas_hps")
ANCH = {1: "Very unlikely", 2: "Unlikely", 3: "Not confirmed", 4: "Likely", 5: "Very likely"}


def main():
    doc = docx.Document(mod.mendeley_fetch("z9w44pc4dp", "Information support file.docx", mod.RAW_DIR))
    t = doc.tables[-2]  # the 37-item questionnaire numbered 1-37 (the last table is the 16-item CFA subset)
    items = {}
    for r in t.rows:
        cells = [c.text.strip() for c in r.cells]
        if re.fullmatch(r"\d+", cells[0]):
            items[int(cells[0])] = " ".join(cells[1].split())
    assert sorted(items) == list(range(1, 38)), sorted(items)
    table = "le_2024_digicas_hps"
    rows = [row(table, f"{table}_1", f"Q{k}", "Digital Competence Assessment Scale for Health Professions Students (DigiCAS-HPS), 37 items", "", r, items[k], option_text=ANCH[r])
            for k in range(1, 38) for r in ANCH]
    write(table, rows)


if __name__ == "__main__":
    main()
