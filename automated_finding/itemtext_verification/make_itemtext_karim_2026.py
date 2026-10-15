#!/usr/bin/env python3
"""Item text for karim_2026_mhl (figshare 10.6084/m9.figshare.34001664). English administration
(the deposited questionnaire 8_S1_Questionnaire.pdf is in English).

Cheap case: data/karim_2026_mhl.py stems() reads the .sav variable labels (English stems) and value
labels (five anchors); the item code is the deposit's own column name.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("karim_2026_mhl")
TABLE = "karim_2026_mhl"


def main():
    rows = []
    for code, stem, vl in mod.stems():
        for r in sorted(vl):
            rows.append(row(TABLE, f"{TABLE}_1", code, "Mental Health Literacy questionnaire (MHLq), 16 agreement items",
                            "", r, stem, option_text=vl[r]))
    write(TABLE, rows)


if __name__ == "__main__":
    main()
