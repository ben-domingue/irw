#!/usr/bin/env python3
"""Item text for zhang_2025_parent_literacy_beliefs (Q4-Q28) and zhang_2025_child_preliteracy (Q29-Q41), Zenodo
14795430. The deposited "parent survey questions.docx" prints the 41 questions under the numbers that are the data
column names (Q<k>), so the mapping is the document's own. The sample is mainland-Chinese kindergarten parents and
only the English questionnaire is deposited, so the English wording ships in the _translated columns with item_text
blank (oliveira_2026 / sakal_2026 precedent), language zho. Scale: 1 strongly disagree - 6 strongly agree, only the
endpoints labelled."""
import re
import zipfile
from _itemtext_writer_c import HERE, row, write

DOCX = HERE / "runs" / "raw" / "zenodo_14795430" / "parent survey questions.docx"
INSTR = "Please indicate to what extent you agree or disagree each of the following statements: 1 = strongly disagree; 6 = strongly agree."
SECTIONS = [("Parental expectations", 4, 7), ("Parent role construction", 8, 11), ("Parent self-efficacy", 12, 15),
            ("Parent-teacher communication", 16, 19), ("Parent-child interaction", 20, 24), ("Home pre-literacy resources", 25, 28),
            ("Pre-literacy disposition", 29, 33), ("Pre-reading", 34, 37), ("Pre-writing", 38, 41)]
OPT = {1: "strongly disagree", 6: "strongly agree"}


def questions():
    xml = zipfile.ZipFile(DOCX).read("word/document.xml").decode("utf8")
    paras = [re.sub(r"<[^>]+>", "", p).strip() for p in re.split(r"</w:p>", xml)]
    q = {}
    for p in paras:
        m = re.match(r"^(\d+)\.\s+(.*)$", p)
        if m:
            q[int(m.group(1))] = m.group(2).strip()
    assert set(q) == set(range(1, 42)), sorted(q)
    return q


def main():
    q = questions()
    for table, lo, hi in (("zhang_2025_parent_literacy_beliefs", 4, 28), ("zhang_2025_child_preliteracy", 29, 41)):
        rows = []
        for sec_i, (name, a, b) in enumerate([s for s in SECTIONS if lo <= s[1] and s[2] <= hi], 1):
            for k in range(a, b + 1):
                for r in range(1, 7):
                    rows.append(row(table, f"{table}_{sec_i}", f"Q{k}", "Parent questionnaire on pre-literacy beliefs, practices and child pre-literacy (Jiang & Zhang)",
                                    "zho", r, "", option_text="", instructions="", section_prompt="",
                                    item_text_tr=q[k], option_text_tr=OPT.get(r, ""), instructions_tr=INSTR, section_prompt_tr=name))
        write(table, rows)


if __name__ == "__main__":
    main()
