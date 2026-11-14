#!/usr/bin/env python3
"""Item text for yousuf_2026_osce_experience and yousuf_2026_osce_discrepancy
(Zenodo 10.5281/zenodo.21407793, OSCE_Psychometric_Data_FINAL..sav).

Mapping basis: data_labels. Item codes are the .sav variable names unchanged (S1-S5, V1-V5, P1-P5,
E1-E6, O1-O4, D1-D5; data/yousuf_2026_osce_experience.py melts them by name). Each variable label is
the item's question; each item's value labels are its five anchors (all five labelled). Sections
follow the deposit's scoring key: station quality, fairness/validity, procedures, physical
environment (E1-E3), examination stress (E4-E6), perceived outcomes, perceived discrepancies.

Text source: study_materials. Two stems searched verbatim ("Was the number of OSCE stations
appropriate", "Was there a discrepancy between what was taught and what was tested"): no published
match, so the 30-item questionnaire is study-authored under the deposit's CC BY 4.0 (register row
YOUSUF-OSCE, ship). Administered in English (the deposit's questionnaire and labels are English).

Run: SAV=<OSCE_Psychometric_Data_FINAL..sav> RESP_DIR=<irw_output> OUT_DIR=<itemtext_output>
     python3 make_itemtext_yousuf_2026.py
"""
import csv
import os
from pathlib import Path

import pandas as pd
import pyreadstat

INST = "OSCE experience questionnaire (Yousuf et al. 2026, Citycot University, Somalia)"
SECTIONS = [("station_quality", "S", range(1, 6)), ("fairness_validity", "V", range(1, 6)),
            ("procedures", "P", range(1, 6)), ("physical_environment", "E", range(1, 4)),
            ("examination_stress", "E", range(4, 7)), ("perceived_outcomes", "O", range(1, 5)),
            ("perceived_discrepancies", "D", range(1, 6))]


def main():
    _, meta = pyreadstat.read_sav(os.environ["SAV"], metadataonly=True)
    by_table = {"yousuf_2026_osce_experience": [], "yousuf_2026_osce_discrepancy": []}
    for sec, pre, nums in SECTIONS:
        table = "yousuf_2026_osce_discrepancy" if pre == "D" else "yousuf_2026_osce_experience"
        for i in nums:
            item = f"{pre}{i}"
            stem = meta.column_names_to_labels[item].strip()
            vl = meta.variable_value_labels[item]
            assert sorted(vl) == [1.0, 2.0, 3.0, 4.0, 5.0], item
            for v in range(1, 6):
                by_table[table].append({
                    "table": table, "section_id": f"{table}_{sec}", "item": item, "instrument": INST,
                    "language": "", "instructions": "", "section_prompt": "", "item_text": stem,
                    "correct_response": "", "option_text": vl[float(v)], "resp": v,
                    "instructions_translated": "", "section_prompt_translated": "",
                    "item_text_translated": "", "option_text_translated": ""})
    for table, rows in by_table.items():
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
