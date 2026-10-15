#!/usr/bin/env python3
"""Item text for guerrero_zambrano_2026_ai_use / _data_mgmt / _adaptation (figshare 33187878). Spanish stems
and anchors from sheet Codigos_y_claves, keyed by column name. Spanish administration (Ecuadorian
teachers); English in the _translated columns is IRW's."""
from _itemtext_writer_c import load_script, row, write

mod = load_script("guerrero_zambrano_2026_ai_teaching")
EN = {"UP1": "I integrate AI tools into my teaching activities.",
      "UP2": "I select AI tools according to specific pedagogical objectives.",
      "UP3": "I use automated assessment tools to support my students' learning.",
      "GD1": "I use educational data to analyse my students' performance.",
      "GD2": "I identify learning patterns using digital tools.",
      "GD3": "I make pedagogical decisions based on information obtained from data.",
      "AI1": "I personalise learning activities according to my students' needs.",
      "AI2": "I use digital tools to improve educational inclusion.",
      "AI3": "I adapt the pace of teaching through the use of technology."}
ANCH_EN = {1: "Strongly disagree", 2: "Disagree", 3: "Neither agree nor disagree", 4: "Agree", 5: "Strongly agree"}
NAME = {"ai_use": "Pedagogical use of artificial intelligence (Uso pedagogico), 3 items",
        "data_mgmt": "Educational data management (Gestion de datos), 3 items",
        "adaptation": "Technology-supported adaptation and inclusion (Adaptacion e inclusion), 3 items"}


def main():
    stems, anchors = mod.codebook()
    for k, cols in mod.BLOCKS.items():
        table = f"guerrero_zambrano_2026_{k}"
        rows = [row(table, f"{table}_1", c, NAME[k], "Spanish", r, stems[c], option_text=anchors[r],
                    item_text_tr=EN[c], option_text_tr=ANCH_EN[r]) for c in cols for r in range(1, 6)]
        write(table, rows)


if __name__ == "__main__":
    main()
