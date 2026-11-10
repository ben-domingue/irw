#!/usr/bin/env python3
"""Item text for aljabry_2026_msg_ffq (10.1371/journal.pone.0360433, PLOS SI,
CC BY 4.0).

Only the food frequency table ships. The same deposit's YFAS 2.0 adaptation,
BES selection and PSS-4 are third-party instruments: PSS is register `block`,
YFAS 2.0 and BES are register `hold` (rows written 2026-11-09). See
data/aljabry_2026_msg_eating.py.

Source: the S2 File (the deposit CSV, a Google Forms export). Each FFQ column
header is the shared stem, then the food in brackets, English then Arabic
("... [Instant Noodles       ??????]"); the Arabic half was lost to '?' in the
CSV's encoding. data/aljabry_2026_msg_eating.py derives each item code from
that bracketed English food name (a slug, matched by name, not by position),
so code and text are tied by the deposit's own header. Option labels are the
English half of each cell value ("1-3 times per month      1-3 ????"), mapped
0..4 by the processing script's FFQ_MAP, in the order the S1 questionnaire
prints them.

Language: the form was bilingual -- every question and option printed in
English and Arabic side by side (S1 File) -- so `language` lists both and the
base fields hold the English half, which respondents read. The Arabic half is
in the S1 PDF only; it is not shipped, because pdftotext output of that PDF
reorders the lam-alef ligature (e.g. 'الأسبوع' comes out as 'األسبوع'), so a
transcription from it would not be verbatim.

Rights: the food list and the frequency stem are study-authored (the article
cites no FFQ source; a register row ALJABRY-FFQ records it) and ship under the
article's CC BY 4.0.

Run: RESP_DIR=<dir> RAW=<S2 csv> python3 make_itemtext_aljabry_2026.py
"""
import csv
import os
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
RAW = os.environ.get("RAW", "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0360433.s002")
TABLE = "aljabry_2026_msg_ffq"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]
INSTRUMENT = ("Food frequency questionnaire for MSG-rich processed foods "
              "(study-authored; Al Jabry et al. 2026)")
# the processing script's (header key, item code) pairs, in header order
FFQ = [("Instant Noodles", "ffq_instant_noodles"),
       ("Potato Chips", "ffq_potato_chips"),
       ("Flavored Crackers", "ffq_flavored_crackers"),
       ("Fast Food Burgers", "ffq_fast_food_burgers"),
       ("Fried Chicken", "ffq_fried_chicken"),
       ("Soy Sauce", "ffq_soy_sauce"),
       ("Salad Dressings", "ffq_salad_dressings"),
       ("Bouillon Cubes", "ffq_bouillon_cubes"),
       ("Seasoning Packets", "ffq_seasoning_packets"),
       ("Pretzels", "ffq_pretzels"),
       ("Chinese Takeout", "ffq_chinese_takeout"),
       ("Condiments", "ffq_condiments"),
       ("Pre-Packaged Deli Meats", "ffq_deli_meats"),
       ("Cheese-Flavored Popcorn", "ffq_cheese_popcorn"),
       ("Pizza", "ffq_pizza"),
       ("Nacho Cheese Sauce", "ffq_nacho_cheese_sauce"),
       ("Tomato Paste", "ffq_tomato_paste")]
FFQ_MAP = {"Never": 0, "1-3 times per month": 1, "1-2 times per week": 2,
           "3-4 times per week": 3, "5 or more times per week": 4}


def english(v):
    """English half of a bilingual cell or bracket ('Never      ?????' -> 'Never')."""
    s = re.split(r"\s{3,}|\?", str(v).strip())[0]
    return re.sub(r"\s+", " ", s).strip()


def main():
    raw = pd.read_csv(RAW)
    cols = list(raw.columns)
    stem = cols[5].split("\n")[0].strip()
    assert stem == ("Please indicate how often, on average, you have consumed "
                    "each food over the past 12 months."), stem
    rows = []
    for j, (key, code) in enumerate(FFQ):
        c = cols[5 + j]
        assert c.split("\n")[0].strip() == stem, c[:120]
        food = english(c[c.index("[") + 1:].rstrip("]"))
        assert food.startswith(key), (key, food)
        seen = {english(v) for v in raw[c]}
        assert seen <= set(FFQ_MAP), (code, seen - set(FFQ_MAP))
        for lab in FFQ_MAP:
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": code,
                         "instrument": INSTRUMENT, "language": "English; Arabic",
                         "instructions": stem, "section_prompt": "",
                         "item_text": food, "correct_response": "",
                         "option_text": lab, "resp": FFQ_MAP[lab],
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
