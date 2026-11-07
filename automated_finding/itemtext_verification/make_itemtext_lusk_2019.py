#!/usr/bin/env python3
"""Item text for the five lusk_2019_* tables (10.1371/journal.pone.0223098,
Harvard Dataverse doi:10.7910/DVN/IEHI3U, CC0).

Source: the deposit's own "CRA Survey Codebook.pdf" (datafile 3594770), the
Qualtrics print of the questionnaire, which gives each block's question, the
row labels with their Qualtrics codes, and the column labels with their codes.
Transcribed by hand from the PDF (pdftotext -layout), joining the row labels
that the PDF wraps across lines. "cholrine" (Q9 washing item) is the
codebook's own spelling and is kept. Administered in English to U.S. adults,
so there are no language or _translated columns.

THE DEPOSIT RENUMBERED TWO BLOCKS. The codebook's Qualtrics codes skip numbers
(Q9: 1-9, 12, 13, 15; Q28: 1-5, 7-10), but data_to_share_2.csv numbers those
blocks consecutively (Q9_1-Q9_12; Q28_1-Q28_9). So:
  deposit Q9_10 / Q9_11 / Q9_12 = codebook Q9_12 (starch) / Q9_13 (vegetable
    oil) / Q9_15 (washing)
  deposit Q28_6 / Q28_7 / Q28_8 / Q28_9 = codebook Q28_7 (convenient) /
    Q28_8 (sustainable) / Q28_9 (individual needs) / Q28_10 (the "click
    somewhat agree" attention check, constant 27 = Somewhat Agree; not in the
    response table)
Q13, Q14 and Q18 keep the codebook's numbers (Q14 skips 6 in both). The
mapping below is in the DEPOSIT's codes, which are what the response tables
carry as `item`. It is checked against the deposit's topline results by
verify_lusk_2019.R.

Response codes are the codebook's. For Q28 the codebook codes the scale 24-28;
data/lusk_2019_healthy_foods.py ships resp = code - 23, so the options are
listed against 1-5 here.

Rights: the questionnaire is the study's own (Lusk's survey for the Corn
Refiners Association, deposited by the author under CC0); no published
instrument. See itemtext_provenance.csv.

Run: RESP_DIR=<dir holding lusk_2019_*.csv> python3 make_itemtext_lusk_2019.py
"""
import csv
import os
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]
INSTRUMENT = "Consumer beliefs about natural and healthy foods survey (Lusk 2019, CRA survey)"
AGREE = ["Strongly Disagree", "Somewhat Disagree", "Neither Agree nor Disagree", "Somewhat Agree",
         "Strongly Agree"]
NATURAL = ["Natural", "Neither Natural or Not", "Not Natural"]
HEALTHY = ["Healthy", "Neither Healthy nor Unhealthy", "Unhealthy"]

BLOCKS = {
    "lusk_2019_natural_processing": (
        "If a food was produced with the following processes or practices, would you consider the food "
        "to be natural or not natural?", NATURAL, {
            "Q9_1": "Fermentation (e.g., sauerkraut, yogurt, bread, beer)",
            "Q9_2": "Added enzymes to improve texture (e.g., in cheese or bread)",
            "Q9_3": "Chopped (e.g., baby carrots, sliced apples, cut watermelon)",
            "Q9_4": "Preserved with sugar, salt, or vinegar",
            "Q9_5": "Preserved by canning, freezing, pasteurization, or smoking",
            "Q9_6": "Preserved with benzoates, nitrites, sulphites, or sorbates",
            "Q9_7": "Flavor enhanced with sugar, salt, or smoking",
            "Q9_8": "Flavor enhanced with MSG, guanylic acid, or Monopotassium glutamate",
            "Q9_9": "Appearance altered through decoloring or bleaching (e.g., flour, sugar, rice)",
            "Q9_10": "Extracted starch from corn, potatoes, or wheat",            # codebook Q9_12
            "Q9_11": "Vegetable oil from pressed grains like soybeans, corn, or canola",  # codebook Q9_13
            "Q9_12": "Washing (e.g., cleaning grains or fruits and vegetables using organic acids or cholrine)",
            # codebook Q9_15
        }),
    "lusk_2019_natural_farming": (
        "If a food was produced from a grain, oilseed, fruit, or vegetable that was grown or farmed using "
        "the following processes or practices, would you consider the food to be natural or not natural?",
        NATURAL, {
            "Q13_1": "seeds created with genetic engineering or GMOs",
            "Q13_2": "hybrid seeds",
            "Q13_3": "seeds created using gene editing",
            "Q13_4": "seeds created using mutagenesis",
            "Q13_5": "crops sprayed with synthetic pesticides like glyphosate or chlorpyrifos",
            "Q13_6": "crops sprayed with natural pesticides like copper sulfate or bacillus thuringiensis",
            "Q13_7": "crops grown indoors in greenhouses",
            "Q13_8": "hydroponically grown crops",
            "Q13_9": "organically grown crops",
        }),
    "lusk_2019_natural_beliefs": (
        "To what extent do you agree or disagree with each of the following statements?", AGREE, {
            "Q14_1": "Natural food is healthier",
            "Q14_2": "Natural food is better for the environment",
            "Q14_3": "Natural food is tastier",
            "Q14_4": "Natural food is more affordable",
            "Q14_5": "Natural food is safer to eat",
            "Q14_7": "Natural food is more convenient to eat",
            "Q14_8": "Natural food is more sustainable",
        }),
    "lusk_2019_healthy_foods": (
        "Do you consider each of the following foods to be healthy or unhealthy for you?", HEALTHY, {
            "Q18_1": "Fresh fruit", "Q18_2": "Frozen fruit", "Q18_3": "Canned fruit",
            "Q18_4": "Fresh vegetables", "Q18_5": "Frozen vegetables", "Q18_6": "Canned vegetables",
            "Q18_7": "Beef", "Q18_8": "Milk", "Q18_9": "Eggs", "Q18_10": "Chicken",
            "Q18_11": "Bakery and cereal items", "Q18_12": "Vegetable oil", "Q18_13": "Fish",
            "Q18_14": "Candy", "Q18_15": "Cheese",
        }),
    "lusk_2019_healthy_beliefs": (
        "To what extent do you agree or disagree with each of the following statements?", AGREE, {
            "Q28_1": "Healthy food is more natural",
            "Q28_2": "Healthy food is better for the environment",
            "Q28_3": "Healthy food is tastier",
            "Q28_4": "Healthy food is more affordable",
            "Q28_5": "Healthy food is safer to eat",
            "Q28_6": "Healthy food is more convenient to eat",                     # codebook Q28_7
            "Q28_7": "Healthy food is more sustainable",                           # codebook Q28_8
            "Q28_8": "Individual needs determine whether various foods are healthy for an individual",
            # codebook Q28_9
        }),
}


def write(table, rows):
    resp = pd.read_csv(RESP_DIR / f"{table}.csv")
    got_items, want_items = {r["item"] for r in rows}, set(resp["item"].astype(str))
    assert got_items == want_items, (table, got_items ^ want_items)
    got_resp, want_resp = {int(r["resp"]) for r in rows}, set(resp["resp"].astype(int))
    assert got_resp == want_resp, (table, got_resp ^ want_resp)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{table}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{path.name}: {len(rows)} rows, {len(got_items)} items, {len(got_resp)} response options")


def main():
    for table, (question, options, items) in BLOCKS.items():
        rows = [{"table": table, "section_id": f"{table}_1", "item": code, "instrument": INSTRUMENT,
                 "instructions": question, "section_prompt": "", "item_text": text, "correct_response": "",
                 "option_text": opt, "resp": k}
                for code, text in items.items() for k, opt in enumerate(options, start=1)]
        write(table, rows)


if __name__ == "__main__":
    main()
