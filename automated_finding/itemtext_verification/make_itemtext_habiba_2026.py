#!/usr/bin/env python3
"""Item text for habiba_2026_ai_tourism (Mendeley 10.17632/cb4y7z9g2s). The Google Forms export's
column headers are "<Construct> [<CODE>: <stem>]" and carry the scale line "1 = Strongly Disagree |
... | 5 = Strongly Agree"; data/habiba_2026_ai_tourism.py stems() parses them. English instrument;
administered language not stated (left blank).
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("habiba_2026_ai_tourism")
TABLE = "habiba_2026_ai_tourism"


def main():
    rows = []
    for code, construct, stem, anch in mod.stems():
        for r in sorted(anch):
            rows.append(row(TABLE, f"{TABLE}_1", code, "Tourists' attitudes toward AI-powered recommendation systems (TAM/UTAUT), 32 items",
                            "", r, stem, option_text=anch[r], section_prompt=construct))
    write(TABLE, rows)


if __name__ == "__main__":
    main()
