#!/usr/bin/env python3
"""Item text for khan_2019_moral_identity (DVN/F3EHOL) and khan_2020_moral_identity / khan_2020_identity_importance
(DVN/IHJQSV). English Qualtrics-style .sav files, Pakistani samples; stems = variable labels, anchors = value labels,
item code = the column name (no renaming in data/khan_2019_moral_identity.py, data/khan_2020_identity.py)."""
import pyreadstat
from _itemtext_writer_c import HERE, row, write

RAW = HERE / "runs" / "raw"
MID_PROMPT = ("Listed below are some characteristics that may describe a person: caring, compassionate, fair, "
              "friendly, generous, hardworking, helpful, honest, kind. Think about how a person with these "
              "characteristics would think, feel and act, then answer the following.")
MID_INSTR = "Moral Identity Measure (Aquino & Reed 2002), 10 agreement items"


def build(table, path, items, instrument, prompt=""):
    d, m = pyreadstat.read_sav(str(path))
    rows = []
    for c in items:
        stem = m.column_names_to_labels[c].replace("(R)", "").strip()
        vl = m.variable_value_labels[c]
        for r in sorted(vl):
            rows.append(row(table, f"{table}_1", c, instrument, "eng", int(r), stem, option_text=vl[r], section_prompt=prompt))
    write(table, rows)


def main():
    mid = [f"MID{i}" for i in range(1, 11)]
    build("khan_2019_moral_identity", RAW / "dvn_F3EHOL" / "Combined Dataset_SID_MID_March2019_Final.sav", mid, MID_INSTR, MID_PROMPT)
    p2 = RAW / "dvn_IHJQSV" / "Dataset_Study 2.sav"
    build("khan_2020_moral_identity", p2, mid, MID_INSTR, MID_PROMPT)
    d, m = pyreadstat.read_sav(str(p2))
    sipi = [c for c in d.columns if (c.startswith("SI") or c.startswith("PI")) and c[2:].isdigit()]
    build("khan_2020_identity_importance", p2, sipi, "Aspects of identity: social (SI) and personal (PI) identity importance, 16 items")


if __name__ == "__main__":
    main()
