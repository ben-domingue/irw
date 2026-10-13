#!/usr/bin/env python3
"""Item text for rathod_2026_dass21 (Harvard Dataverse 10.7910/DVN/IRIKMP). English
administration (Namibia; the survey manual is in English).

Cheap case: the .dta variable labels are the DASS-21 statements; data/rathod_2026_drought_dass21.py
exposes stems() -> (code, statement) pairs, so the item code is the deposit's own column name.
The items carry no value labels; the 0-3 anchors are the DASS's own (Lovibond & Lovibond),
recorded as such in provenance.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "rathod_2026_drought_dass21.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]
TABLE = "rathod_2026_dass21"
OPTIONS = {0: "Did not apply to me at all", 1: "Applied to me to some degree, or some of the time",
           2: "Applied to me to a considerable degree, or a good part of time",
           3: "Applied to me very much, or most of the time"}
INSTRUCTIONS = ("Please read each statement and select a number 0, 1, 2 or 3 which indicates how much the "
                "statement applied to you over the past week.")


def main():
    spec = importlib.util.spec_from_file_location("rathod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    resp = pd.read_csv(RESP_DIR / f"{TABLE}.csv")
    codes = mod.stems()
    assert {c for c, _ in codes} == set(resp["item"]) and set(resp["resp"].unique()) <= set(OPTIONS)
    rows = []
    for code, text in codes:
        for r, o in OPTIONS.items():
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": code,
                         "instrument": "Depression Anxiety Stress Scales (DASS-21)",
                         "instructions": INSTRUCTIONS, "section_prompt": "", "item_text": text,
                         "correct_response": "", "option_text": o, "resp": r})
    p = OUT_DIR / f"{TABLE}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows, {len(codes)} items")


if __name__ == "__main__":
    main()
