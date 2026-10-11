#!/usr/bin/env python3
"""Item text for the four darko_2025_* tables (Harvard Dataverse 10.7910/DVN/MDDYTI;
paper 10.1186/s13104-025-07307-y). English administration (Ghanaian senior high schools).

Cheap case: the deposit's column headers ARE the statements and the cells hold the option
labels. data/darko_2025_substance_use.py assigns item codes <block>_<k> in header order and
exposes the exact (code, header) pairs via stems(), imported here, so each item's text is
the header its responses sat under; options are the labels the script mapped to integers
(FIVE / FOUR), asserted against the observed resp set of the staged CSV.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "darko_2025_substance_use.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]
META = {
    "rses": ("Rosenberg Self-Esteem Scale", ""),
    "reasons": ("Reasons for substance use (study-specific)",
                "Indicate your level of agreement with each of the following reasons for substance use."),
    "perceptions": ("Perceptions of substance use (study-specific)",
                    "Indicate your level of agreement with each of the following statements about substance use."),
    "interventions": ("School interventions against substance use (study-specific)",
                      "Indicate your level of agreement with each of the following interventions."),
}


def main():
    spec = importlib.util.spec_from_file_location("darko", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for block, (instrument, instructions) in META.items():
        table = f"darko_2025_{block}"
        opts = {v: k for k, v in mod.BLOCKS[block][2].items()}
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        codes = mod.stems(block)
        assert {c for c, _ in codes} == set(resp["item"]), table
        assert set(resp["resp"].unique()) <= set(opts), table
        rows = []
        for code, header in codes:
            for r, o in sorted(opts.items()):
                rows.append({"table": table, "section_id": f"{table}_1", "item": code,
                             "instrument": instrument, "instructions": instructions,
                             "section_prompt": "", "item_text": header, "correct_response": "",
                             "option_text": o, "resp": r})
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {len(codes)} items")


if __name__ == "__main__":
    main()
