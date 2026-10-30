#!/usr/bin/env python3
# Item text for the li_2024_vr_* tables (see li_2024_vr_exhibition.py).
#
# Source: the column headers of journal.pone.0308267.s001 themselves, which
# carry the item code and the full English wording in one string ("INT1 The VR
# can respond quickly to my actions"). CC BY 4.0 Supporting Information of
# 10.1371/journal.pone.0308267.
#
# THE MAPPING IS THE STRONGEST KIND THERE IS: the wording and the response
# column are the same object. There is no join, no printed order and no
# position -- a stem cannot be attached to the wrong column because it is not
# attached at all, it is read off the column. The response script and this one
# share one parser (parse_headers) so the two can never drift.
#
# The items are the authors' own English rendering of a TAM/VR-acceptance
# battery; the article reproduces them as Table 1 "Questionnaire" and the
# deposit reproduces them as headers, both under the article's CC BY 4.0.
#
# OPTION TEXT IS NOT SHIPPED AT ALL, which is a stronger statement than the
# blank middles elsewhere in this batch. The article gives "5-point scale"
# with "strongly disagree" and "strongly agree" as the endpoints but never
# says WHICH END IS 1. So even the two anchors cannot be attached to a resp
# value without guessing the direction, and attaching them backwards would be
# worse than leaving them off. All five resp values carry a row with empty
# option_text so the resp sets still match; the direction question is recorded
# in the response tables' descriptions and in itemtext_provenance.

import csv
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from li_2024_vr_exhibition import CONSTRUCTS, parse_headers  # noqa: E402

RAW = os.environ.get("LIVR_RAW", "journal.pone.0308267_S1_Data.xlsx")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")

INSTRUMENT = ("Li & Lv (2024) online VR exhibition acceptance questionnaire "
              "(Table 1), a TAM extension with interactivity, immersion and "
              "presence")
INSTR = ("Thinking about your experience of the Liangzhu Museum online VR "
         "exhibition, please rate your agreement with each statement on a "
         "five-point scale from strongly disagree to strongly agree.")
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def build():
    df = pd.read_excel(RAW, nrows=1)
    parsed = parse_headers(df)
    assert len(parsed) == 27, len(parsed)

    os.makedirs(OUT, exist_ok=True)
    n_items = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        items = sorted([(code, text) for code, (_, p, text) in parsed.items()
                        if p == prefix], key=lambda t: int(t[0][len(prefix):]))
        assert len(items) == n, (name, len(items), n)
        rows = []
        for code, text in items:
            for resp in range(1, 6):
                rows.append({"table": name, "section_id": name + "_1",
                             "item": code, "instrument": INSTRUMENT,
                             "instructions": INSTR, "section_prompt": label,
                             "item_text": text, "correct_response": "",
                             "option_text": "", "resp": resp})
        with open(os.path.join(OUT, name + "__items.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        n_items += len(items)
        print(f"{name}__items.csv: {len(items)} items, {len(rows)} rows")
    assert n_items == 27, n_items
    print(f"8 item-text tables, {n_items} items, read straight off the "
          f"deposit's own column headers")


if __name__ == "__main__":
    build()
