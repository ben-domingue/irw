#!/usr/bin/env python3
# Item text for five of the seven bredbenner_2019_* tables (see
# bredbenner_2019_video_abstracts.py for the response tables).
#
# Source: the column headers of journal.pone.0224697.s007 themselves, which
# carry the full question text including the bracketed option label that
# Google Forms appends for a matrix row. CC BY 4.0 Supporting Information.
#
# THE TWO COMPREHENSION TABLES ARE NOT COVERED. Their five true/false
# statements exist in the deposit only as a concatenated free-text "check all
# that apply" answer, and the six scored columns are unnamed -- the deposit's
# own total fixes WHICH SIX columns are the scored items without fixing which
# is which. A mapping gap, not a rights one.
#
# OPTION TEXT IS THE AUTHORS' OWN CODING, not an inference. The deposit stores
# the first preference battery twice, as words and as 0-4, so the five labels
# map one-to-one onto the five numbers; the response script asserts that
# bijection and this script reuses it, so the option labels shipped here are
# exactly the words the authors coded as those numbers.

import csv
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bredbenner_2019_video_abstracts import (  # noqa: E402
    PREF_LABELS, PREF_NUM, RAW, REACT, UPDATES)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")
INSTRUMENT = ("Bredbenner & Simon (2019) science-summary experiment "
              "questionnaire")
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]
OPTIONS = sorted(((v, k) for k, v in PREF_LABELS.items()))


def tidy(h):
    return " ".join(str(h).split())


def build():
    df = pd.read_excel(RAW, sheet_name="Sheet1", nrows=1)
    c = list(df.columns)

    # (table, [(item code, header)], instructions)
    jobs = [
        ("bredbenner_2019_format_preference",
         [(p.lower().replace(" ", "_"), None) for p in PREF_NUM],
         "Please say how much you prefer the following ways of getting new "
         "scientific information."),
        ("bredbenner_2019_updates_outside_field",
         [(f"OUT{i}", c[j]) for i, j in enumerate(UPDATES[:4], 1)], None),
        ("bredbenner_2019_updates_in_field",
         [(f"IN{i}", c[j]) for i, j in enumerate(UPDATES[4:], 1)], None),
        ("bredbenner_2019_reactions_cohn",
         list(zip(["enjoy", "understand", "want_updates"],
                  [c[39], c[41], c[43]])), None),
        ("bredbenner_2019_reactions_takata",
         list(zip(["enjoy", "understand", "want_updates"],
                  [c[55], c[57], c[59]])), None),
    ]
    # the five format-preference items are named by their numeric twin's
    # header ('Video', 'Graphic', ...), with the question in the text column
    pref_headers = dict(zip([p.lower().replace(" ", "_") for p in PREF_NUM],
                            [c[8], c[10], c[12], c[14], c[16]]))

    os.makedirs(OUT, exist_ok=True)
    n_items = 0
    for name, items, instr in jobs:
        rows = []
        for code, header in items:
            header = header if header is not None else pref_headers[code]
            text = tidy(header)
            if instr is None:
                # "<stem>: [<option>]" -- keep the whole thing as item_text
                # and use the stem before the bracket as the section prompt
                prompt = tidy(text.split("[")[0]).rstrip(": ")
            else:
                prompt = tidy(instr)
            for resp, label in OPTIONS:
                rows.append({"table": name, "section_id": name + "_1",
                             "item": code, "instrument": INSTRUMENT,
                             "instructions": instr or prompt,
                             "section_prompt": prompt, "item_text": text,
                             "correct_response": "", "option_text": label,
                             "resp": resp})
        with open(os.path.join(OUT, name + "__items.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        n_items += len(items)
        print(f"{name}__items.csv: {len(items)} items, {len(rows)} rows")
    assert n_items == 20, n_items
    print("5 item-text tables, 20 items, read off the deposit's own column "
          "headers with the authors' own option coding")


if __name__ == "__main__":
    build()
