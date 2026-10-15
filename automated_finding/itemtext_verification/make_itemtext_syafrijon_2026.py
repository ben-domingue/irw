#!/usr/bin/env python3
"""Item text for syafrijon_2026_digital_use and syafrijon_2026_sdc (Mendeley 6wxhpybm8b). Stems transcribed
from the deposited Questionnaire.pdf (Section B), keyed by the printed code = column name; anchors from
Codebook.pdf (anchor 1 never endorsed, see OBSERVED). The questionnaire is deposited in English; administration language not stated -> blank."""
from _itemtext_writer_c import load_script, row, write

mod = load_script("syafrijon_2026_student_digital_competence")
STEM = {
    "TA1": "I actively keep up with developments in digital technology in the field of education.",
    "TA2": "I am eager to share my experiences using digital technology with my friends.",
    "TE1": "I always use technology responsibly and respectfully, avoiding the spread of false or negative information.",
    "TE2": "I understand the legal rules regarding technology use and refrain from illegally stealing others’ information.",
    "TO1": "I can handle common issues related to applications that support learning (e.g., PowerPoint, MS Word, etc.).",
    "TO2": "I can use digital learning technology in the classroom (e.g., computers, projectors, etc.).",
    "TO3": "I can use technology for at least one subject.",
    "TS1": "I enjoy using digital technology when learning.",
    "TS2": "I enjoy participating in lessons that incorporate technology.",
    "TS3": "I feel satisfied when using technology for learning.",
    "TS4": "I believe using technology is a good choice for learning.",
    "TS5": "I can adapt to learning activities that involve technology.",
    "EU1": "I can quickly find important information using digital technology.",
    "EU2": "I can easily access learning materials through digital technology.",
    "EU3": "I can use applications that support learning (e.g., PowerPoint, MS Word, etc.).",
    "EU4": "I can easily access digital information.",
    "EH1": "I am accustomed to using digital technology to complete my assignments.",
    "EH2": "I feel it is necessary to use digital technology when I study.",
    "EH3": "I am used to finding study materials using digital technology.",
    "EH4": "I will continue to use digital technology for learning in the future.",
    "SDC1": "I can find specific objects or information using search engines (e.g., Google, Yahoo, Bing) by entering relevant keywords.",
    "SDC2": "I can create documents with text, diagrams, tables, and reports using applications (e.g., Excel, PowerPoint, etc.).",
    "SDC3": "I am able to collaborate and communicate with others using various devices, platforms, and digital tools.",
    "SDC4": "I can copy, download, save, and delete various types of digital information.",
    "SDC5": "I can evaluate the accuracy of digital information.",
    "SDC6": "I can effectively manage my digital accounts.",
}
ANCH = {1: "Strongly Disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly Agree"}
INSTR = ("Please indicate the extent to which you agree with each statement. 1 = Strongly Disagree, "
         "2 = Disagree, 3 = Neutral, 4 = Agree, 5 = Strongly Agree")
# No respondent chose 1 on any item, so the resp-set gate (exact match with the staged table) requires the
# option-1 rows to be omitted; the full five-anchor scale is kept in `instructions`.
OBSERVED = range(2, 6)


def main():
    for table, items, name in (("syafrijon_2026_digital_use", mod.USE,
                                "Digital technology use in learning: technology attitudes, ethics, operations, satisfaction, ease of use and e-habits, 20 items"),
                               ("syafrijon_2026_sdc", mod.SDC, "Students' Digital Competence, 6 items")):
        rows = [row(table, f"{table}_1", c, name, "", r, STEM[c], option_text=ANCH[r], instructions=INSTR)
                for c in items for r in OBSERVED]
        write(table, rows)


if __name__ == "__main__":
    main()
