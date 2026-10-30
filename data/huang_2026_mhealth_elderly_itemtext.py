#!/usr/bin/env python3
# Item text for the huang_2026_mh_* tables (see huang_2026_mhealth_elderly.py).
#
# Source: "Multimedia Appendix 1: Measurement items", S1 File of
# 10.1371/journal.pone.0361137 -- CC BY 4.0 Supporting Information of the
# article. It is a three-column table of construct, items and literature
# source, listing exactly three items per construct in the deposit's own
# order, so the mapping is construct-explicit and the within-construct order
# is the appendix's printed order.
#
# The item codes come from parse_headers() in the response script, so the two
# tables are generated from one assignment of codes to columns and cannot
# drift.
#
# THE ITEMS ARE THE AUTHORS' OWN ADAPTATION. The appendix credits a source per
# construct -- Gefen et al. and Yoon et al. for perceived convenience,
# El-Masry for perceived quality, Davis for usefulness and ease of use, Taylor
# & Todd for attitude, Daghan & Akkoyunlu for behavioural intention, McKnight
# et al. and Pavlou & Gefen for trust, Deng et al. for risk -- but prints only
# the mHealth-specific wording this study administered, never those sources'
# own text. So nothing third-party is reproduced and the article's CC BY
# covers what ships. Register: HUANG-CAI-MHEALTH, ship.
#
# OPTION TEXT: anchors only. The paper labels 1 "totally disagree" and 7
# "totally agree" and nothing in between, so 2-6 ship with option_text empty
# rather than a guessed set of five intermediate labels. All seven resp values
# carry a row so the sets match.
#
# Administered in Chinese to elderly residents of Zhanjiang; the appendix
# publishes the items in English only, so the English is what ships.

import csv
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from huang_2026_mhealth_elderly import (  # noqa: E402
    CONSTRUCTS, RAW, parse_headers)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")
INSTRUMENT = ("Huang & Cai (2026) smartphone mHealth app acceptance "
              "questionnaire (S1 File, Measurement items)")
INSTR = ("Thinking about smartphone mobile medical (mHealth) applications, "
         "please rate your agreement with each statement from 1 (totally "
         "disagree) to 7 (totally agree).")
OPTIONS = [(1, "Totally disagree"), (2, ""), (3, ""), (4, ""), (5, ""),
           (6, ""), (7, "Totally agree")]

# transcribed from S1 File, three per construct, in its printed order
ITEMS = {
 "PCON": ["I can use my smartphone mobile medical application anywhere.",
          "I can use my smartphone to move medical applications at any time.",
          "Smart phone mobile medical application can provide convenience for medical information query."],
 "PQ": ["I think the smartphone mobile medical application provides enough information.",
        "I think the smart phone mobile medical application provides reliable information.",
        "I think the smartphone mobile medical application provides a reliable service."],
 "PU": ["Using a smartphone mobile medical application can meet my medical needs.",
        "Using a smartphone mobile medical application can improve my medical efficiency.",
        "Overall, the smartphone mobile medical application is very useful for my medical treatment."],
 "PEOU": ["I find it easy for me to operate mobile medical applications on smartphones.",
          "It won't take me much time to operate the mobile medical application of smartphone.",
          "Overall, I find the smartphone mobile medical application easy to use."],
 "ATT": ["Using a smartphone mobile medical app is a good idea.",
         "Using a smartphone mobile medical application is a wise idea.",
         "I like the idea of using mobile medical apps on my smartphone."],
 "BI": ["I intend to use smartphone mobile medical applications in the future.",
        "I will use smartphone mobile medical applications in the future.",
        "I will regularly use smartphone mobile medical applications in the future."],
 "PTrust": ["I believe that the smartphone mobile medical application is trustworthy.",
            "I believe that smartphone mobile medical applications are professional.",
            "I believe that smartphone mobile medical applications are reliable."],
 "PRisk": ["I think the smartphone mobile medical application may reveal my personal privacy.",
           "I think the smartphone mobile medical application may use my personal information for other purposes.",
           "I think there are risks in medical payment in smart phone mobile medical application."],
}
SOURCES = {"PCON": "Gefen et al.; Yoon et al.", "PQ": "El-Masry",
           "PU": "Davis", "PEOU": "Davis", "ATT": "Taylor & Todd",
           "BI": "Daghan & Akkoyunlu",
           "PTrust": "McKnight et al.; Pavlou & Gefen", "PRisk": "Deng et al."}
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def build():
    codes = set(parse_headers(pd.read_csv(RAW, nrows=1)).values())
    assert len(codes) == 24, len(codes)

    os.makedirs(OUT, exist_ok=True)
    n_items = 0
    for prefix, (name, label) in CONSTRUCTS.items():
        texts = ITEMS[prefix]
        assert len(texts) == 3, (prefix, len(texts))
        rows = []
        for i, text in enumerate(texts, 1):
            code = f"{prefix}{i}"
            assert code in codes, f"{code} is not a column in the deposit"
            for resp, lab in OPTIONS:
                rows.append({"table": name, "section_id": name + "_1",
                             "item": code, "instrument": INSTRUMENT,
                             "instructions": INSTR,
                             "section_prompt":
                                 f"{label} (items adapted from "
                                 f"{SOURCES[prefix]})",
                             "item_text": text, "correct_response": "",
                             "option_text": lab, "resp": resp})
        with open(os.path.join(OUT, name + "__items.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        n_items += len(texts)
        print(f"{name}__items.csv: {len(texts)} items, {len(rows)} rows")
    assert n_items == 24, n_items
    print("8 item-text tables, 24 items, every item of every response table")


if __name__ == "__main__":
    build()
