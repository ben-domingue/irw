#!/usr/bin/env python3
"""Item text for hartmann_2026_food_forest_wtp and hartmann_2026_monoculture_health_risk
(Zenodo 10.5281/zenodo.22035305, "26 food forest acceptance.sav").

Mapping basis: data_labels. Item codes are the .sav variable names unchanged (WillingnessToPay1..4,
MonocultureHealthRisk1..6; data/hartmann_2026_food_forest.py melts them by name). Each variable label
is "<section prompt><separator> <stem>"; the prompt goes to section_prompt and the stem to item_text.
Anchors 1 and 5 are the value labels; 2-4 are labelled only by their number in the file and are left
blank.

Text source: study_materials. Stems searched verbatim: they match no published scale, so they are
study-authored under the deposit's CC BY 4.0. The other three blocks in the file are not shipped here
(nature connectedness = NR-6/CNS stems, need for uniqueness = CNFU short form, both third-party; the
climate-concern questions' source is unidentified).

Run: SAV=<26 food forest acceptance.sav> RESP_DIR=<irw_output> OUT_DIR=<itemtext_output>
     python3 make_itemtext_hartmann_2026.py
"""
import csv
import os
from pathlib import Path

import pandas as pd
import pyreadstat

TABLES = {
    "hartmann_2026_food_forest_wtp": ("WillingnessToPay", 4, "?",
        "Willingness to pay for food forest products (Hartmann 2026, TRANSCLIMA survey)"),
    "hartmann_2026_monoculture_health_risk": ("MonocultureHealthRisk", 6, ":",
        "Perceived health risk of monoculture farming (Hartmann 2026, TRANSCLIMA survey)"),
}


def main():
    _, meta = pyreadstat.read_sav(os.environ["SAV"], metadataonly=True)
    for table, (pre, k, sep, inst) in TABLES.items():
        rows = []
        for i in range(1, k + 1):
            item = f"{pre}{i}"
            lab = meta.column_names_to_labels[item]
            prompt, stem = lab.split(sep, 1)
            prompt, stem = prompt.strip() + sep, stem.strip()
            vl = meta.variable_value_labels[item]
            assert vl[1.0] == "Strongly disagree" and vl[5.0] == "Strongly agree", item
            for v in range(1, 6):
                opt = vl[float(v)] if v in (1, 5) else ""
                rows.append({"table": table, "section_id": f"{table}_1", "item": item, "instrument": inst,
                             "language": "English", "instructions": "", "section_prompt": prompt,
                             "item_text": stem, "correct_response": "", "option_text": opt, "resp": v,
                             "instructions_translated": "", "section_prompt_translated": "",
                             "item_text_translated": "", "option_text_translated": ""})
        resp = pd.read_csv(Path(os.environ["RESP_DIR"]) / f"{table}.csv")
        assert {r["item"] for r in rows} == set(resp["item"]), table
        assert {r["resp"] for r in rows} >= set(resp["resp"]), table
        out = Path(os.environ["OUT_DIR"]) / f"{table}__items.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{out}: {len(rows)} rows")


if __name__ == "__main__":
    main()
