#!/usr/bin/env python3
"""Item text for the four khan_2021_* tables (Harvard Dataverse 10.7910/DVN/GQEFOI). English
administration (Qualtrics-style .sav with English labels; Pakistani sample).

Cheap case: data/khan_2021_identity.py stems() reads each item's .sav variable label (stem) and value
labels (seven anchors); the item code is the deposit's own column name.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("khan_2021_identity")
INSTR = {"khan_2021_place_identity": "Place identity, 6 agreement items",
         "khan_2021_moral_identity": "Moral Identity Measure (Aquino & Reed 2002), 10 agreement items",
         "khan_2021_identity_importance": "Aspects of identity: social (SI) and personal (PI) identity importance, 16 items",
         "khan_2021_religious_orientation": "Religious Orientation (intrinsic / extrinsic), 14 agreement items"}
MID_PROMPT = ("Listed below are some characteristics that may describe a person: caring, compassionate, fair, "
              "friendly, generous, hardworking, helpful, honest, kind. Think about how a person with these "
              "characteristics would think, feel and act, then answer the following.")


def main():
    rows = {t: [] for t in INSTR}
    for table, code, stem, vl in mod.stems():
        stem = stem.replace("(R)", "").replace("(Reversed)", "").strip()
        for r in sorted(vl):
            rows[table].append(row(table, f"{table}_1", code, INSTR[table], "", r, stem, option_text=vl[r],
                                   section_prompt=MID_PROMPT if table == "khan_2021_moral_identity" else ""))
    for t, rs in rows.items():
        write(t, rs)


if __name__ == "__main__":
    main()
