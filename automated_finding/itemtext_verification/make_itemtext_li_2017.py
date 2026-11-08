#!/usr/bin/env python3
"""Item text for li_2017_saq (10.1371/journal.pone.0179486, PLOS SI S1 File,
CC BY 4.0).

Source: the S1 File's second sheet, "data description", a codebook written by
the study that lists each data column (t1 ... w4) against the English SAQ
statement it holds ("1. Nurse input is well received in this clinical
area.") and the response codes ("1 = disagree strongly, 2 = disagree
slightly, 3 = neutral, 4 = agree slightly, 5 = agree strongly, 999 = missing
data and answered not applicable"). data/li_2017_saq_heilongjiang.py keeps the
deposit's column names as item codes, so code and text are tied by the
deposit itself (no positional step).

Language: the survey was administered in Chinese (the authors translated and
back-translated the original English SAQ; Methods). The Chinese wording is not
in the deposit or the article's SI, so the codebook's English ships in the
base fields (fallback: language=Chinese, _translated columns empty).

Transcription: the leading item number ("1. ") and the scoring marker
"(R)*" on items 2 and 11 are removed; the wording is otherwise as printed,
including "ar sufficient" (item 26) and "errors of other" (item 13).

Rights: SAQ short form, register row SAQ (ship, UTHealth CHQS blanket grant).

Run: RESP_DIR=<dir> RAW=<S1 xlsx> python3 make_itemtext_li_2017.py
"""
import csv
import os
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
RAW = os.environ.get("RAW", "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0179486.s001")
TABLE = "li_2017_saq"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]
INSTRUMENT = "Safety Attitudes Questionnaire, short form (SAQ-SF), Chinese version (Li et al. 2017, Heilongjiang)"
CODES = "1 = disagree strongly, 2 = disagree slightly, 3 = neutral, 4 = agree slightly, 5 = agree strongly, 999 = missing data and answered not applicable"


def main():
    cb = pd.read_excel(RAW, sheet_name="data description", header=None)
    cb = cb.iloc[2:, 1:4]
    cb.columns = ["var", "desc", "value"]
    cb = cb[cb["var"].str.match(r"^(t|s|j|st|p|w)\d$", na=False)]
    assert len(cb) == 30
    assert (cb["value"] == CODES).all()
    opts = [(int(k), lab.strip()) for k, lab in re.findall(r"(\d+) = ([a-z ]+?)(?:,|$)", CODES) if int(k) < 10]
    assert [k for k, _ in opts] == [1, 2, 3, 4, 5]
    rows = []
    for k, (var, desc) in enumerate(zip(cb["var"], cb["desc"]), start=1):
        m = re.match(r"^(\d+)\. (.*?)(?: \(R\)\*)?$", desc.strip())
        assert m and int(m.group(1)) == k, desc
        for resp, lab in opts:
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": var,
                         "instrument": INSTRUMENT, "language": "Chinese",
                         "instructions": "", "section_prompt": "", "item_text": m.group(2),
                         "correct_response": "", "option_text": lab, "resp": resp,
                         "instructions_translated": "", "section_prompt_translated": "",
                         "item_text_translated": "", "option_text_translated": ""})
    resp = pd.read_csv(RESP_DIR / f"{TABLE}.csv")
    assert {r["item"] for r in rows} == set(resp["item"])
    assert {r["resp"] for r in rows} == set(resp["resp"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / f"{TABLE}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{TABLE}__items.csv: {len(rows)} rows, {len(rows) // 5} items")
    for r in rows[::5]:
        print("   ", r["item"], "|", r["item_text"])


if __name__ == "__main__":
    main()
