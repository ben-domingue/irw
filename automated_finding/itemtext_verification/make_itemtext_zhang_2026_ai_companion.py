#!/usr/bin/env python3
"""Item text for zhang_2026_ai_companion (figshare 10.6084/m9.figshare.32576487.v1). The
deposit's column headers are the 27 statements in English, numbered with the Chinese
enumeration comma ("10、"), one ending in a Chinese full stop -- a Chinese administration
whose Chinese wording is not in the deposit. Fallback: language=Chinese, English in the base
fields, _translated empty, text_source=translated_substitute.

Cheap case: data/zhang_2026_ai_companion.py derives item q<k> from header "<k>、..." and
exposes the (code, stem) pairs via stems(), imported here. The anchors of the 1-5 scale are
not in the file, so option_text is blank for every point.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "zhang_2026_ai_companion.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
T = "zhang_2026_ai_companion"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "section_prompt_translated", "item_text",
        "item_text_translated", "correct_response", "option_text", "option_text_translated", "resp"]


def main():
    spec = importlib.util.spec_from_file_location("zhang", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    resp = pd.read_csv(RESP_DIR / f"{T}.csv")
    pairs = mod.stems()
    assert {c for c, _ in pairs} == set(resp["item"])
    assert set(resp["resp"]) <= set(range(1, 6))
    rows = []
    for code, stem in pairs:
        stem = stem.rstrip("。").strip()
        for r in range(1, 6):
            rows.append({"table": T, "section_id": f"{T}_1", "item": code,
                         "instrument": "Emotional companion AI user experience and behaviour survey (27 items, study-specific)",
                         "language": "Chinese", "instructions": "", "instructions_translated": "",
                         "section_prompt": "", "section_prompt_translated": "", "item_text": stem,
                         "item_text_translated": "", "correct_response": "", "option_text": "",
                         "option_text_translated": "", "resp": r})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"{T}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows, {len(pairs)} items")
    for c, s in pairs[:3] + pairs[-2:]:
        print("  ", c, "|", s[:90])


if __name__ == "__main__":
    main()
