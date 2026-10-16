#!/usr/bin/env python3
"""Item text for niu_2026_ai_recommendation (Mendeley 10.17632/wkmm4t7bwh, Study3.sav). The .sav
variable labels are the English stems; no value labels on the items, so option_text is blank
(seven-point scale, endpoints undocumented in the file). English administration (online consumer
sample, English labels).
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("niu_2026_ai_recommendation")
TABLE = "niu_2026_ai_recommendation"


def main():
    rows = []
    for code, stem in mod.stems():
        for r in range(1, 8):
            rows.append(row(TABLE, f"{TABLE}_1", code, "Post-stimulus ratings of an AI product recommendation (Study 3), 28 items, 1-7", "", r, stem))
    write(TABLE, rows)


if __name__ == "__main__":
    main()
