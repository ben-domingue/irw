#!/usr/bin/env python3
"""Item text for cisneros_2023_digital_competence (Zenodo 10055380). Spanish stems = the .sav variable
labels (printed "D1.1. " number stripped), anchors = the five level names in the value labels (0/25/50/
75/100 -> 0-4 in the table). Spanish administration; English in the _translated columns is IRW's.
"""
import re

from _itemtext_writer_c import load_script, row, write

mod = load_script("cisneros_2023_teaching_digital_competence")
LEVEL_ES = {0: "No iniciado", 1: "Principiante", 2: "Medio", 3: "Experto", 4: "Transformador"}
LEVEL_EN = {0: "Not started", 1: "Beginner", 2: "Intermediate", 3: "Expert", 4: "Transformer"}
EN = {"D1.1": "Teaching planning and digital competence", "D1.2": "Digital technologies as facilitators of learning",
      "D1.3": "Information processing and knowledge creation", "D1.4": "Attention to diversity (special educational needs)",
      "D1.5": "Assessment, tutoring and monitoring of students", "D1.6": "Methodological line of the academic unit",
      "D2.1": "Learning environments", "D2.2": "Management of digital technologies and applications",
      "D2.3": "Spaces with digital technologies in the academic unit", "D2.4": "Projects for incorporating digital technologies",
      "D2.5": "Digital technology infrastructure", "D3.1": "Ethics and security", "D3.2": "Digital inclusion",
      "D3.3": "Communication, dissemination and transfer of knowledge", "D3.4": "Digital content and the educational community",
      "D3.5": "Digital identity of the institution", "D4.1": "Open access to information, creation and dissemination of teaching material",
      "D4.2": "Leadership in the use of digital technologies", "D4.3": "Continuing education",
      "D4.4": "Virtual learning communities: formal, non-formal and informal", "D4.5": "Personal learning environment (PLE)",
      "D4.6": "Digital identity and presence"}


def main():
    labels, vlabels = mod.labels()
    table = "cisneros_2023_digital_competence"
    rows = []
    for c in mod.ITEMS:
        stem = re.sub(r"^D\d\.\d\.\s*", "", labels[c]).strip()
        vl = {mod.LEVEL[k]: v for k, v in vlabels[c].items()}
        assert vl == LEVEL_ES, (c, vl)
        for r in range(5):
            rows.append(row(table, f"{table}_1", c, "Teaching digital competence self-assessment, 22 indicators in four dimensions", "Spanish",
                            r, stem, option_text=LEVEL_ES[r], item_text_tr=EN[c], option_text_tr=LEVEL_EN[r]))
    write(table, rows)


if __name__ == "__main__":
    main()
