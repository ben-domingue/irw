#!/usr/bin/env python3
"""Item text for rajeev_2025_superstition / _panas / _bigfive (Harvard Dataverse
10.7910/DVN/33B2DP). English administration (India).

Cheap case: the column headers ARE the statements; data/rajeev_2025_superstition_affect_personality.py
assigns <prefix>_k by header order and asserts each header's leading number equals k, exposing
stems(block) -> (code, statement) pairs, imported here. The file has no option labels, so
option_text is blank on every scale point (one row per item x point).
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "rajeev_2025_superstition_affect_personality.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]


def main():
    spec = importlib.util.spec_from_file_location("rajeev", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for block, (_, _, instrument) in mod.BLOCKS.items():
        table = f"rajeev_2025_{block}"
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        codes = mod.stems(block)
        assert {c for c, _ in codes} == set(resp["item"]), table
        assert set(resp["resp"].unique()) <= set(range(1, 6)), table
        rows = [{"table": table, "section_id": f"{table}_1", "item": code, "instrument": instrument,
                 "instructions": "", "section_prompt": "", "item_text": text, "correct_response": "",
                 "option_text": "", "resp": r} for code, text in codes for r in range(1, 6)]
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {len(codes)} items")


if __name__ == "__main__":
    main()
