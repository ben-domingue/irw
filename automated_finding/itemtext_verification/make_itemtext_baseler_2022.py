#!/usr/bin/env python3
"""Item text for baseler_2022_{cognitive,sensory} (10.1371/journal.pone.0269353,
PLOS SI S1 File, CC BY 4.0).

Source, two levels:
- the S1 File's own column headers, which carry each item's wording and, for
  six cognitive items, a bracketed example ("Memory_Remembering_things\\n\\n(for
  example, problems remembering names, appointments ...)"). The item code is
  the header cut at its first line break and lower-cased
  (data/baseler_2022_covid_cognitive_symptoms.py), so code and header are tied
  reversibly. item_text is the header's words with the block prefix and the
  underscores removed, plus the bracketed example verbatim where the header
  has one.
- the article's Methods, for the stem and the four response labels: "rate
  their responses subjectively (using 'None', 'Mild', 'Moderate' or 'Severe')
  to the following 16 questions: 'During the COVID-19 pandemic, have you had
  MORE problems with: ...' In addition, we used the same scale to assess
  whether they had more problems with vision, hearing, smell, taste, touch or
  pain, balance, and dizziness." Stored 1-4 in that order (the deposit's codes
  run 1-4 and the paper lists the labels in ascending severity).

Rights: the 16 questions are the authors' own (designed for this Qualtrics
survey, no instrument cited; a verbatim search of two stems found no
published scale). Administered in English; no _translated columns.

Run: RESP_DIR=<dir> RAW=<S1 xlsx> python3 make_itemtext_baseler_2022.py
"""
import csv
import os
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
RAW = os.environ.get("RAW", "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0269353.s001")
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]
INSTRUMENT = "Self-rated cognitive and sensory problems during the COVID-19 pandemic (Baseler et al. 2022, CORONA survey)"
STEM = "During the COVID-19 pandemic, have you had MORE problems with:"
OPTIONS = ["None", "Mild", "Moderate", "Severe"]


def words(header):
    first, _, rest = header.partition("\n")
    stem = re.sub(r"^(Memory|Sensory)_", "", first.strip()).replace("_", " ").strip()
    example = re.sub(r"\s+", " ", rest).strip()
    return f"{stem} {example}" if example else stem


def main():
    df = pd.read_excel(RAW, sheet_name="S1_data", nrows=1)
    for table, prefix in (("baseler_2022_cognitive", "Memory_"), ("baseler_2022_sensory", "Sensory_")):
        rows = []
        for h in [c for c in df.columns if str(c).startswith(prefix)]:
            code = h.split("\n")[0].strip().lower()
            rows += [{"table": table, "section_id": f"{table}_1", "item": code, "instrument": INSTRUMENT,
                      "instructions": STEM, "section_prompt": "", "item_text": words(h), "correct_response": "",
                      "option_text": opt, "resp": k} for k, opt in enumerate(OPTIONS, start=1)]
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        assert {r["item"] for r in rows} == set(resp["item"]), table
        assert {r["resp"] for r in rows} == set(resp["resp"]), table
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUT_DIR / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{table}__items.csv: {len(rows)} rows, {len(rows) // 4} items")
        for r in rows[::4]:
            print("   ", r["item"], "|", r["item_text"])


if __name__ == "__main__":
    main()
