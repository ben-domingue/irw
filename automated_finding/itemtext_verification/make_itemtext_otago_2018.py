"""Build otago_2018_library_support__items.csv from the deposit's own transcript.

Source: "Transcript of questions asked.docx" in figshare 7464938, the
questionnaire as fielded. Its Q22 block is a Qualtrics matrix whose eight rows
are printed with the row ids "(1)".."(8)" -- which are exactly the suffixes of
the Q22_1..Q22_8 columns in the data file. The stems are read out of the docx
here rather than retyped, so the shipped wording is the deposit's.

The administration was English, so `language` and the `_translated` columns are
left out entirely rather than emitted empty.

option_text is populated for the two LABELLED scale points only. The form
printed "1 (most preferred)" and "5 (least preferred)" with bare "2", "3", "4"
in between: those three are unlabelled midpoints and must stay blank rather
than be padded with their own numbers.

Usage:
  python3 make_itemtext_otago_2018.py <Transcript of questions asked.docx> <outdir>
"""
from __future__ import annotations

import csv
import html
import re
import sys
import zipfile
from pathlib import Path

DOCX = Path(sys.argv[1])
OUT = Path(sys.argv[2])

TABLE = "otago_2018_library_support"
INSTRUMENT = ("Postgraduate Support at Otago student questionnaire, Q22 "
              "(Library support preferences) -- Research Support Unit "
              "Library, University of Otago (2018)")
INSTRUCTIONS = (
    "The following questions relate specifically to Library academic support "
    "for postgraduate students at the University of Otago.\n\n"
    "What is the best way the Library can support you? Please rank with 1 "
    "being the most preferred and 5 the least preferred.")
OPTIONS = {1: "1 (most preferred)", 2: "", 3: "", 4: "",
           5: "5 (least preferred)"}

FIELDS = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text",
          "resp"]


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    xml = re.sub(r"</w:p>", "\n", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def q22_stems(text: str) -> dict[int, str]:
    """The eight matrix rows between the Q22 stem and the Q35 that follows it."""
    start = text.index("Q22 What is the best way the Library can support you")
    end = text.index("Q35", start)
    block = text[start:end]
    found = {}
    for line in block.splitlines():
        line = line.strip()
        m = re.fullmatch(r"(.+?)\s*\((\d)\)", line)
        if not m:
            continue
        label, num = m.group(1).strip(), int(m.group(2))
        # The five column headers ("1 (most preferred) (1)", "2 (2)", ...)
        # match this shape too; the row stems are the ones that are not just
        # a scale point.
        if re.fullmatch(r"\d(\s*\(.*\))?", label):
            continue
        found[num] = label
    assert sorted(found) == list(range(1, 9)), sorted(found)
    return found


def main() -> None:
    stems = q22_stems(docx_text(DOCX))
    rows = []
    for num in range(1, 9):
        for resp, option in OPTIONS.items():
            rows.append({
                "table": TABLE,
                "section_id": f"{TABLE}_1",
                "item": f"Q22_{num}",
                "instrument": INSTRUMENT,
                "instructions": INSTRUCTIONS,
                "section_prompt": "",
                "item_text": stems[num],
                "correct_response": "",
                "option_text": option,
                "resp": resp,
            })
    path = OUT / f"{TABLE}__items.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    for num in range(1, 9):
        print(f"  Q22_{num}  {stems[num]}")
    print(f"{path.name}: {len(rows)} rows, 8 items, resp 1-5")


if __name__ == "__main__":
    main()
