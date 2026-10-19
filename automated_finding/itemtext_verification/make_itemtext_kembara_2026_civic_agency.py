#!/usr/bin/env python3
"""Item text for kembara_2026_civic_agency (#3077, 2026-10-19a batch).

SOURCE: sheet "A6. Survey Instrument" of the deposit's own workbook
(figshare 32414913, "CSE_Appendix_Data_Statistics.xlsx"), the same file the
response data comes from. It is a four-column table -- Code / Dimension /
Item (Indonesian) / Item (English) -- whose codes Q1-Q6 are exactly the item
columns of sheet "A1. Raw Data". So the code-to-text tie is STATED by the
source, not inferred from order.

IDENTIFICATION, done from the stems and not from the deposit's label. All six
were searched: they match no published instrument. They are the study's own,
one per named dimension -- structural powerlessness, pedagogical stagnation,
civic self-efficacy, structural civic competence, the expression-construction
gap, and civic knowledge valuation -- and the construct vocabulary
("structural civic agency", "Beyond Active Citizenship") is this paper's. So
there is no third-party instrument here and nothing for
itemtext/instrument_rights_register.csv to rule on: rights are the depositors'
own material under the record's CC BY 4.0. That is what makes this table the
one in its batch that ships without waiting for a ruling.

LANGUAGE: administered in Indonesian, so the Indonesian stems are the base
`item_text` and the authors' OWN English -- not an IRW translation -- is
`item_text_translated`. No `translation_source` or issues-page callout is owed
for an author-supplied translation.

THE DIMENSION NAMES ARE NOT SHIPPED AS TEXT. Each item is its own dimension, so
a per-dimension `section_id` would be six sections of one item each, and the
dimension name is a construct label rather than anything a respondent read --
it belongs in neither `section_prompt` nor `instructions`. One trivial
`section_id` is used and the dimensions are recorded in the provenance note.

OPTIONS: the appendix gives the scale as "Scale 1=Strongly Disagree to
5=Strongly Agree" -- the two endpoints only, and in English only. So resp 1
and 5 carry those labels in `option_text_translated`, with `option_text` empty
because the administered Indonesian anchors are nowhere in the deposit, and
resp 2-4 are empty in both: an unlabelled midpoint must stay blank rather than
be padded with its own number. `audit_batch.R` reports blank option_text; that
is the expected result here, not a defect.

INSTRUCTIONS: none. The appendix's "Part A: Likert Scale Items" is its own
heading, not text shown to respondents, so `instructions` is blank rather than
filled with a paraphrase. Part B of the same instrument is an open-ended
design task whose response is free text; it is not in the response table and
is not an item here.
"""
import csv
import os
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent / "itemtext_output"
RAW = Path(os.environ.get(
    "IRW_RAW_DIR",
    HERE.parent / "runs" / "figshare_batch" / "32414913" / "raw"))
FNAME = "CSE_Appendix_Data_Statistics.xlsx"
TABLE = "kembara_2026_civic_agency"
SECTION = f"{TABLE}_1"
INSTRUMENT = ("Structural civic agency and wellbeing in higher education "
              "(study-authored, six single-item dimensions; CSE-26-0013, "
              "\"Beyond Active Citizenship\")")
LANGUAGE = "Indonesian"
ANCHORS_EN = {1: "Strongly Disagree", 5: "Strongly Agree"}
RESP_VALUES = [1, 2, 3, 4, 5]

COLUMNS = ["table", "section_id", "item", "instrument", "language",
           "instructions", "instructions_translated", "section_prompt",
           "section_prompt_translated", "item_text", "item_text_translated",
           "correct_response", "option_text", "option_text_translated", "resp"]


def main():
    d = pd.read_excel(RAW / FNAME, sheet_name="A6. Survey Instrument",
                      header=None)
    stems = {}
    for _, r in d.iterrows():
        code = str(r.iloc[0]).strip()
        if not code.startswith("Q") or code == "Code":
            continue
        ind, eng = str(r.iloc[2]).strip(), str(r.iloc[3]).strip()
        assert ind and ind != "nan" and eng and eng != "nan", code
        stems[code] = (ind, eng)
    assert sorted(stems) == [f"Q{i}" for i in range(1, 7)], sorted(stems)

    rows = []
    for code in sorted(stems, key=lambda c: int(c[1:])):
        ind, eng = stems[code]
        for resp in RESP_VALUES:
            rows.append({
                "table": TABLE,
                "section_id": SECTION,
                "item": code,
                "instrument": INSTRUMENT,
                "language": LANGUAGE,
                "instructions": "",
                "instructions_translated": "",
                "section_prompt": "",
                "section_prompt_translated": "",
                "item_text": ind,
                "item_text_translated": eng,
                "correct_response": "",
                "option_text": "",
                "option_text_translated": ANCHORS_EN.get(resp, ""),
                "resp": resp,
            })

    resp_csv = HERE.parent / "irw_output" / f"{TABLE}.csv"
    with open(resp_csv, newline="", encoding="utf-8") as f:
        live = list(csv.DictReader(f))
    assert {r["item"] for r in live} == set(stems), "item sets differ"
    assert {int(r["resp"]) for r in live} == set(RESP_VALUES), "resp sets differ"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{TABLE}__items.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{os.path.basename(out)}: {len(rows)} rows, {len(stems)} items x "
          f"{len(RESP_VALUES)} options")


if __name__ == "__main__":
    main()
