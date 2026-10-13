"""Shared row writer for the repos 2026-10-11 C builders (make_itemtext_*.py in this folder)."""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DATA = HERE.parent / "data"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]


def load_script(stem: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(stem, DATA / f"{stem}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def row(table, section, item, instrument, language, resp, item_text, option_text="", instructions="",
        section_prompt="", item_text_tr="", option_text_tr="", instructions_tr="", section_prompt_tr=""):
    return {"table": table, "section_id": section, "item": item, "instrument": instrument, "language": language,
            "instructions": instructions, "section_prompt": section_prompt, "item_text": item_text,
            "correct_response": "", "option_text": option_text, "resp": resp,
            "instructions_translated": instructions_tr, "section_prompt_translated": section_prompt_tr,
            "item_text_translated": item_text_tr, "option_text_translated": option_text_tr}


def write(table, rows, resp_codes=None):
    import pandas as pd
    resp = pd.read_csv(RESP_DIR / f"{table}.csv")
    assert {r["item"] for r in rows} == set(resp["item"]), table
    assert set(resp["resp"].unique()) <= {r["resp"] for r in rows}, table
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"{table}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows, {len({r['item'] for r in rows})} items")
