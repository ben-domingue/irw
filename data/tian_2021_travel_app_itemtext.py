#!/usr/bin/env python3
# Item text for the tian_2021_app_* tables (see
# tian_2021_travel_app_engagement.py for the response tables).
#
# Source: "Appendix A", S1 File of 10.1371/journal.pone.0248460 -- CC BY 4.0
# Supporting Information of the article. It is a .doc (Word 97-2003), not a
# .docx, so the usual zipfile route fails on it; it was read with
# `libreoffice --headless --convert-to txt`. The appendix lists each item
# under its construct WITH ITS CODE (EOU1, COM1, ... PI3), so the mapping is
# code-level.
#
# TWO CODES ARE CROSSWALKED, and this file is where that is recorded:
#   appendix PI1, PI2, PI3  ->  deposit PE1, PE2, PE3   (purchase intention;
#     PI appears nowhere in the data and PE nowhere in the appendix, and each
#     is the only unmatched block on its side, so the identity is forced)
#   appendix BE2            ->  deposit BE22            (a typo in the header)
# The response tables keep the deposit's codes, so this table must too, or the
# join breaks. CROSSWALK below is the whole of the discrepancy.
#
# ONE ITEM SHIPS WITH A CORRUPTION THAT IS THE SOURCE'S. COM1 reads "This
# travel app is compatible with my travel p References." in the published
# appendix -- an OCR-or-paste artefact of "preferences", present in the
# original .doc and not introduced by the conversion. It ships verbatim:
# silently repairing a published item would make IRW's text differ from the
# article's with nothing to say so.
#
# Option text: anchors only. The paper labels 1 "strongly disagree" and 5
# "strongly agree" and nothing between.

import csv
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tian_2021_travel_app_engagement import (  # noqa: E402
    CONSTRUCTS, RAW, blocks_of)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")
INSTRUMENT = ("Tian, Shi & Cheng (2021) mobile travel app engagement "
              "questionnaire (S1 File, Appendix A)")
INSTR = ("Thinking about the mobile travel app you use, please rate your "
         "agreement with each statement from 1 (strongly disagree) to 5 "
         "(strongly agree).")
OPTIONS = [(1, "Strongly disagree"), (2, ""), (3, ""), (4, ""),
           (5, "Strongly agree")]
# appendix code -> deposit code, for the two that differ
CROSSWALK = {"PI1": "PE1", "PI2": "PE2", "PI3": "PE3", "BE2": "BE22"}

# transcribed from Appendix A, in its printed order
ITEMS = [
 ("EOU1", "This travel app is easy to use."),
 ("EOU2", "Learning how to use this travel app is easy for me."),
 ("EOU3", "I would imagine that most people would learn to use this app very quickly."),
 ("COM1", "This travel app is compatible with my travel p References."),
 ("COM2", "This travel app suits my travel needs."),
 ("COM3", "This travel app fits well with my travel needs."),
 ("UIA1", "The interface design of this travel app is beautiful."),
 ("UIA2", "The interface design of this travel app is aesthetically pleasing."),
 ("UIA3", "The interface design of this travel app is visually appealing."),
 ("CE1", "This information of the travel can attract my attention"),
 ("CE2", "This information of the travel can stimulate my interest"),
 ("CE3", "This information of the travel can get me to think a lot"),
 ("AE1", "When I use the travel app, I feel very happy"),
 ("AE2", "When I use the travel app, I feel very positive."),
 ("AE3", "When I use the travel app, I feel very good."),
 ("BE1", "I spend a lot of time using the travel app, compared to other travel apps"),
 ("BE2", "Whenever I’m using the travel app, I usually use this travel app."),
 ("BE3", "The travel app is one of the travel apps I usually use."),
 ("PI1", "I intend to purchase the travel products recommended by the travel app"),
 ("PI2", "I will consider purchasing travel products recommended by the travel app"),
 ("PI3", "I may purchase travel products recommended by the travel app."),
]
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def build():
    blocks = blocks_of(pd.read_excel(RAW, nrows=1))
    in_data = {c for cols in blocks.values() for c in cols}

    rows_by_table = {}
    for app_code, text in ITEMS:
        code = CROSSWALK.get(app_code, app_code)
        assert code in in_data, f"{app_code} -> {code} is not a data column"
        prefix = next(p for p in CONSTRUCTS if code in blocks[p])
        name, label = CONSTRUCTS[prefix]
        note = (f"{label}" if code == app_code
                else f"{label} (appendix code {app_code})")
        for resp, lab in OPTIONS:
            rows_by_table.setdefault(name, []).append(
                {"table": name, "section_id": name + "_1", "item": code,
                 "instrument": INSTRUMENT, "instructions": INSTR,
                 "section_prompt": note, "item_text": text,
                 "correct_response": "", "option_text": lab, "resp": resp})

    os.makedirs(OUT, exist_ok=True)
    n_items = 0
    for name, rows in rows_by_table.items():
        with open(os.path.join(OUT, name + "__items.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        n = len({r["item"] for r in rows})
        n_items += n
        print(f"{name}__items.csv: {n} items, {len(rows)} rows")
    assert n_items == 21, n_items
    print("7 item-text tables, 21 items, from Appendix A with the PI->PE and "
          "BE2->BE22 crosswalk applied")


if __name__ == "__main__":
    build()
