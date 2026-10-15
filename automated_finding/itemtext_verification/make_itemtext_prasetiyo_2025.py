#!/usr/bin/env python3
"""Item text for prasetiyo_2025_digital_citizenship (Mendeley Data 10.17632/h4gcfmbk5c).

Cheap case: the deposited questionnaire (.docx, English) prints each statement followed by its
sub-dimension and code, "Digital Inclusion (DI1)", and the xlsx header row carries the same codes, so
the mapping is by the questionnaire's own code, not by position. Anchors 1 Strongly Disagree .. 5
Strongly Agree. Administration language not stated (Indonesian students); `language` left blank.
"""
import re
import zipfile

from _itemtext_writer_c import HERE, load_script, row, write

mod = load_script("prasetiyo_2025_digital_citizenship")
DOCX = (HERE / "runs" / "raw" / "10_17632_h4gcfmbk5c" /
        "Mendeley Data_Questionnaire on Multidimensional Digital Citizenship Competence among Indonesian Civic Education Students.docx")
TABLE = "prasetiyo_2025_digital_citizenship"
OPTS = {1: "Strongly Disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly Agree"}
INSTRUCTIONS = ("Please select the response that best reflects your reality and experiences by placing a check mark "
                "in the appropriate box.")


def main():
    x = zipfile.ZipFile(DOCX).read("word/document.xml").decode()
    ps = [re.sub("<[^>]+>", "", m) for m in re.findall(r"<w:p[ >].*?</w:p>", x, flags=re.S)]
    ps = [p.replace("&amp;", "&").strip() for p in ps if p.strip()]
    stems = {}
    for a, b in zip(ps, ps[1:]):
        m = re.search(r"\((DI\d|IDC\d|CE\d|DE\d)\)$", b)
        if m:
            stems[m.group(1)] = a
    assert set(stems) == set(mod.ITEMS), set(mod.ITEMS) ^ set(stems)
    rows = []
    for code in mod.ITEMS:
        for r in sorted(OPTS):
            rows.append(row(TABLE, f"{TABLE}_1", code, "Multidimensional digital citizenship competence (DICE+ framework), 13 items",
                            "", r, stems[code], option_text=OPTS[r], instructions=INSTRUCTIONS))
    write(TABLE, rows)


if __name__ == "__main__":
    main()
