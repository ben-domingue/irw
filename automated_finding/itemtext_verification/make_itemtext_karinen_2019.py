#!/usr/bin/env python3
"""Item text for the four karinen_2019_* tables (Mendeley rgy8jngdrz, DataForJESP.sav, Qualtrics export, English US
administration). Stems = variable labels, anchors = value labels; item codes are the column names (kept by
data/karinen_2019_disgust_immigration.py). The TDDS labels embed the common stem ("How disgusting do you find the
following experience or concept?") before the item, which moves to section_prompt. Value labels that are a bare
number ship blank; labels like "Not at all disgusting\\n0" and "Completely disagree\\n\\n1\\n" ship as the words."""
import re
import pyreadstat
from _itemtext_writer_c import HERE, row, write, load_script

RAW = HERE / "runs" / "raw" / "mendeley_rgy8jngdrz" / "DataForJESP.sav"
mod = load_script("karinen_2019_disgust_immigration")
TDDS_PROMPT = "How disgusting do you find the following experience or concept?"
TABLES = {"karinen_2019_tdds_pathogen": (mod.TDDS, "Three Domain Disgust Scale, pathogen subscale, 7 items", TDDS_PROMPT),
          "karinen_2019_sdo7": (mod.SDO, "Social Dominance Orientation scale (SDO7), 16 agreement items", ""),
          "karinen_2019_traditionalism": (mod.ASC, "Traditionalism / adherence to social conventions, 6 agreement items", ""),
          "karinen_2019_immigrant_attitudes": (mod.IMM, "Attitudes toward the described immigrant (Ngolo), 6 agreement items", "")}


def anchor(label: str) -> str:
    words = re.sub(r"\s*\d+\s*$", "", label.strip()).strip()
    return "" if re.fullmatch(r"\d*", words) else words


def main():
    d, m = pyreadstat.read_sav(str(RAW))
    for table, (items, instrument, prompt) in TABLES.items():
        rows = []
        for c in items:
            stem = m.column_names_to_labels[c].strip()
            if prompt and stem.startswith(prompt):
                stem = stem[len(prompt):].strip()
            vl = m.variable_value_labels[c]
            for r in sorted(vl):
                rows.append(row(table, f"{table}_1", c, instrument, "eng", int(r), stem, option_text=anchor(vl[r]), section_prompt=prompt))
        write(table, rows)


if __name__ == "__main__":
    main()
