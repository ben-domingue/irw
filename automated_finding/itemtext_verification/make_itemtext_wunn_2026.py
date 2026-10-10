#!/usr/bin/env python3
"""Item text for wunn_2026_research_competence, wunn_2026_imi and wunn_2026_cognitive_load
(Zenodo 10.5281/zenodo.20494091). German upper-secondary students, administered in German.

Cheap case: the deposit's "Items" sheet lists every item code with its English
("Description") and German ("Beschreibung") wording, and data/wunn_2026_student_lab.py
derives item from the same code (brackets dropped, pre/post letter removed), exposing the
code -> (English, German) map via items_sheet(). German goes in item_text, English in
item_text_translated (both the authors' own). The anchors are not in the sheet (they are in
the deposit's Documentation PDF), so option_text is blank for every scale point.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "wunn_2026_student_lab.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "section_prompt_translated", "item_text",
        "item_text_translated", "correct_response", "option_text", "option_text_translated", "resp"]
META = {"wunn_2026_research_competence": ("Research competence self-assessment (27 items, study-specific)", range(1, 5)),
        "wunn_2026_imi": ("Intrinsic Motivation Inventory, short form (12 items)", range(1, 6)),
        "wunn_2026_cognitive_load": ("Cognitive load scale (intrinsic, germane, extraneous; 8 items)", range(1, 6))}


def main():
    spec = importlib.util.spec_from_file_location("wunn", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    texts = mod.items_sheet()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (instrument, valid) in META.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        assert set(resp["item"]) <= set(texts), set(resp["item"]) - set(texts)
        assert set(resp["resp"]) <= set(valid)
        rows = []
        for it in sorted(resp["item"].unique()):
            en, de = texts[it]
            for r in valid:
                rows.append({"table": table, "section_id": f"{table}_1", "item": it,
                             "instrument": instrument, "language": "German", "instructions": "",
                             "instructions_translated": "", "section_prompt": "",
                             "section_prompt_translated": "", "item_text": de,
                             "item_text_translated": en, "correct_response": "",
                             "option_text": "", "option_text_translated": "", "resp": r})
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {resp['item'].nunique()} items")


if __name__ == "__main__":
    main()
