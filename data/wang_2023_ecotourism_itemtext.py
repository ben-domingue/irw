#!/usr/bin/env python3
# Item text for the wang_2023_eco_* tables (see
# wang_2023_ecotourism_responsibility.py for the response tables).
#
# Source: the column headers of journal.pone.0281119.s001 and .s002
# themselves, which carry the item number and the full English wording. CC BY
# 4.0 Supporting Information of 10.1371/journal.pone.0281119.
#
# THE ITEM CODES EXIST BECAUSE THE SOURCE NUMBERS CANNOT BE USED. The two
# questionnaires number their items 1..18 each and five numbers mean different
# items in the two files, so the response tables key items by WORDING under
# codes derived from it (ECO01.., RES01.., TOU01..). This script imports the
# same code_map from the response script, so the item text and the responses
# are generated from one assignment and cannot drift. The deposit's original
# numbers are kept in section_prompt for traceability, with BOTH numbers given
# for the five items where the two forms disagree.
#
# OPTION TEXT IS NOT SHIPPED. The article never states the number of scale
# points or the anchor labels -- its interpretation bands imply 1-5 and the
# observed range is exactly 1-5, but nothing says which end is which. As with
# li_2024_vr_*, attaching anchors backwards would be worse than leaving them
# off, so all five resp values carry a row with empty option_text.

import csv
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wang_2023_ecotourism_responsibility import (  # noqa: E402
    RAW_R, RAW_T, TABLES, code_map, item_columns)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")
INSTRUMENT = ("Wang et al. (2023) Qilian Mountains National Park ecotourism "
              "and environmentally responsible behaviour questionnaire")
INSTR = ("Please rate your agreement with each statement about ecotourism in "
         "Qilian Mountains National Park.")
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def build():
    ir = item_columns(pd.read_excel(RAW_R, nrows=1))
    it = item_columns(pd.read_excel(RAW_T, nrows=1))
    codes, counters = code_map(ir, it)
    rev = {v: k for k, v in codes.items()}
    num_r = {text: n for n, (_, text) in ir.items()}
    num_t = {text: n for n, (_, text) in it.items()}

    os.makedirs(OUT, exist_ok=True)
    n_items = 0
    for name, prefix, label in TABLES:
        items = sorted([c for c in rev if c.startswith(prefix)])
        assert len(items) == counters[prefix], (name, len(items))
        rows = []
        for code in items:
            text = rev[code]
            where = []
            if text in num_r:
                where.append(f"resident form item {num_r[text]}")
            if text in num_t:
                where.append(f"tourist form item {num_t[text]}")
            for resp in range(1, 6):
                rows.append({"table": name, "section_id": name + "_1",
                             "item": code, "instrument": INSTRUMENT,
                             "instructions": INSTR,
                             "section_prompt": f"{label} ({'; '.join(where)})",
                             "item_text": text, "correct_response": "",
                             "option_text": "", "resp": resp})
        with open(os.path.join(OUT, name + "__items.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        n_items += len(items)
        print(f"{name}__items.csv: {len(items)} items, {len(rows)} rows")
    assert n_items == 20, n_items
    print("3 item-text tables, 20 items, read off the two files' column "
          "headers under the response tables' own code assignment")


if __name__ == "__main__":
    build()
