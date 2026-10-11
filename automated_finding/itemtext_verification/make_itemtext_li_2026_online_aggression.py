#!/usr/bin/env python3
"""Item text for the five li_2026_* tables (Mendeley 10.17632/sjyrmwbcbx). Administered
language not stated in the deposit; the item sheet is in English.

Cheap case: the deposit's second sheet lists each Q-code with its statement and the anchors
"{1, Strongly disagree} ... {7, Strongly agree}"; data/li_2026_online_aggression.py exposes
stems() -> {Q-code: statement} and BLOCKS, so the item code is the deposit's own column name.
Only the two end anchors are labelled, so option_text rows exist for resp 1 and 7 and the
unlabelled midpoints 2-6 are blank.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "li_2026_online_aggression.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]
OPTIONS = {1: "Strongly disagree", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "Strongly agree"}


def main():
    spec = importlib.util.spec_from_file_location("li", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stems = mod.stems()
    for suffix, (nums, instrument) in mod.BLOCKS.items():
        table = f"li_2026_{suffix}"
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        codes = [f"Q{k}" for k in nums]
        assert set(codes) == set(resp["item"]) and set(resp["resp"].unique()) <= set(OPTIONS), table
        rows = []
        for code in codes:
            for r, o in OPTIONS.items():
                rows.append({"table": table, "section_id": f"{table}_1", "item": code, "instrument": instrument,
                             "instructions": "", "section_prompt": "", "item_text": stems[code],
                             "correct_response": "", "option_text": o, "resp": r})
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {len(codes)} items")


if __name__ == "__main__":
    main()
