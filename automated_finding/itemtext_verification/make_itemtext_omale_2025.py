#!/usr/bin/env python3
"""Item text for the six omale_2025_ppd_* tables (Mendeley Data 10.17632/2tzj5m5kp4). English
administration (Nigerian survey, English questionnaire in the variable labels).

Cheap case: data/omale_2025_ppd_help_seeking.py stems() reads the .sav variable labels (stems) and the
value labels (SD/D/U/A/SA, expanded to words); the item code is the deposit's own VARxxxxx name.
VAR00081 and VAR00082 carry the identical label "The newspaper has provided me with information on
postpartum depression." in the deposit; VAR00082 ships with a blank item_text and the table is flagged
for the public issues page rather than guessing a second medium.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("omale_2025_ppd_help_seeking")
INSTR = {"omale_2025_ppd_knowledge": "Knowledge and awareness of postpartum depression",
         "omale_2025_ppd_info_sources": "Sources of information on postpartum depression",
         "omale_2025_ppd_beliefs": "Beliefs about postpartum depression",
         "omale_2025_ppd_norms": "Cultural and subjective norms about postpartum depression",
         "omale_2025_ppd_control": "Perceived control and barriers to seeking help for postpartum depression",
         "omale_2025_ppd_intention": "Intention to seek help for postpartum depression"}
BLANK = {"VAR00082"}


def main():
    for table, items in mod.stems().items():
        rows = []
        for code, stem, vl in items:
            for r in sorted(vl):
                rows.append(row(table, f"{table}_1", code, INSTR[table], "", r, "" if code in BLANK else stem,
                                option_text=vl[r]))
        write(table, rows)


if __name__ == "__main__":
    main()
