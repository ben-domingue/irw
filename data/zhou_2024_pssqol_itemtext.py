#!/usr/bin/env python3
# Item text for three of the four zhou_2024_* tables (see
# zhou_2024_pssqol_chinese.py for the response tables).
#
# Source: the column headers of journal.pone.0313839.s002 themselves. The
# PSS-QoL sheet heads each data column with the item number and its full
# English wording ("13.1Burning sensation in the mouth"), and the ESSPRI
# sheet names its three domains. CC BY 4.0 Supporting Information.
#
# THE SF-12 TABLE IS NOT COVERED. Its columns are called "Item 1".."Item 12"
# and carry no wording, and the instrument is QualityMetric's. A rights hold
# and an availability gap at once.
#
# THE ESSPRI ROWS CARRY THE DEPOSIT'S DOMAIN NAMES, NOT THE INSTRUMENT'S
# PUBLISHED STEMS. The sheet heads its three columns "Pian" (sic), "Fatigue"
# and "Dryness" and gives no question wording. The ESSPRI's actual stems are
# well known, but they are not in this source, so writing them here would be
# recall rather than transcription. The domain names ship instead.
#
# NO OPTION TEXT. The article's readable text labels neither the 0-4 impact
# scale's points nor the symptom items' two values, and the ESSPRI's 0-10
# ratings have no verbal anchors to carry. Every resp value gets a row so the
# sets match, with option_text empty.
#
# The item codes come from item_code() in the response script, so the two
# tables are generated from one assignment and cannot drift.

import csv
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zhou_2024_pssqol_chinese import RAW, HEAD, item_code  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]
PSSQOL = ("PSS-QoL (Primary Sjogren's Syndrome Quality of Life "
          "questionnaire), Chinese version adapted by Zhou et al. (2024)")
ESSPRI = ("EULAR Sjogren's Syndrome Patient Reported Index (ESSPRI)")


def write(name, rows, n_items):
    with open(os.path.join(OUT, name + "__items.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{name}__items.csv: {n_items} items, {len(rows)} rows")


def build():
    p = pd.read_excel(RAW, sheet_name="PSS-QoL", nrows=1)
    os.makedirs(OUT, exist_ok=True)

    items = []
    for c in p.columns:
        m = HEAD.match(str(c).strip())
        if m and m.group(2).strip():
            items.append((float(m.group(1)), item_code(c),
                          re.sub(r"\s+", " ", m.group(2)).strip()))
    sym = [(code, text) for n, code, text in items if 8 <= n < 18]
    imp = [(code, text) for n, code, text in items if n >= 18]
    assert len(sym) == 30 and len(imp) == 14, (len(sym), len(imp))

    rows = [{"table": "zhou_2024_pssqol_symptoms",
             "section_id": "zhou_2024_pssqol_symptoms_1", "item": code,
             "instrument": PSSQOL,
             "instructions": "Please indicate whether you have experienced "
                             "each of the following.",
             "section_prompt": "Symptom presence", "item_text": text,
             "correct_response": "", "option_text": "", "resp": r}
            for code, text in sym for r in (0, 1)]
    write("zhou_2024_pssqol_symptoms", rows, len(sym))

    rows = [{"table": "zhou_2024_pssqol_impact",
             "section_id": "zhou_2024_pssqol_impact_1", "item": code,
             "instrument": PSSQOL,
             "instructions": "Please rate how far each statement applies to "
                             "you.",
             "section_prompt": "Impact on quality of life", "item_text": text,
             "correct_response": "", "option_text": "", "resp": r}
            for code, text in imp for r in range(5)]
    write("zhou_2024_pssqol_impact", rows, len(imp))

    # the deposit names the three domains and nothing more. The ESSPRI's
    # published stems ("How severe has your pain been in the last two
    # weeks?") are NOT transcribed from anything in this source, so what
    # ships is the domain name the deposit actually gives.
    esspri = [("pain", "Pain"), ("fatigue", "Fatigue"), ("dryness", "Dryness")]
    rows = [{"table": "zhou_2024_esspri", "section_id": "zhou_2024_esspri_1",
             "item": code, "instrument": ESSPRI,
             "instructions": "Rate each symptom on a scale from 0 (no "
                             "symptom) to 10 (maximal imaginable symptom).",
             "section_prompt": "ESSPRI domain", "item_text": text,
             "correct_response": "", "option_text": "", "resp": r}
            for code, text in esspri for r in range(11)]
    write("zhou_2024_esspri", rows, len(esspri))
    print("3 item-text tables, 47 items. The SF-12 table is not covered -- "
          "proprietary instrument, no wording in the deposit")


if __name__ == "__main__":
    build()
