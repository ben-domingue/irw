#!/usr/bin/env python3
"""Item text for the three abdulkader_mohamed_2022_* tables (s12889-022-14147-z).

The deposit's column headers ARE the item stems (English; the questionnaire
was administered in English -- Methods: "the questionnaire was written in
English"). The cells are the response labels, so the anchors come from the
same file. Item codes were assigned positionally by
data/abdulkader_mohamed_2022_exercise_kap.py (know_1..9 = columns 0-8,
att_1..10 = columns 9-18, exg_1..5 = columns 28-32); this script re-reads the
same workbook and applies the same positions, so code->header is the script's
own map rather than a reconstruction.

Two deviations from the headers, both disclosed in provenance:
  * Every "no" in the headers was replaced by "2" in the deposit (a find-and-
    replace artefact): "e2ugh", "2rmal", "k2w", "I have 2 time". Restored to
    "enough", "normal", "know", "I have no time" -- the paper's Tables 4/6/7
    print these same items with "no" intact, e.g. "I feel that I have no time
    of my own ...", "Did you know what is exergames?".
  * Surrounding whitespace is stripped. Everything else, including grammar
    ("Aerobic exercise include ...", "an excuse to keep away yourself from
    further exercises exercising more"), is kept as administered.
Option labels are shipped as the respondents saw them in the export, except the
knowledge block's "Netural", which is the export's misspelling of "Neutral"
(Methods: "agree, neutral, disagree") and is corrected.
"""
import csv
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9472413/supplementaryFiles"
XLSX = "12889_2022_14147_MOESM1_ESM.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp"]

INSTR = ("Knowledge, Attitude, and Practice regarding Exercise and Exergames "
         "Experiences questionnaire (KAP-EEE, adapted from Fabunmi et al.)")
BLOCKS = [
    ("abdulkader_mohamed_2022_exer_knowledge", range(0, 9), "know",
     f"{INSTR} -- Part 2, knowledge about exercise",
     [(1, "Disagree"), (2, "Neutral"), (3, "Agree")]),
    ("abdulkader_mohamed_2022_exer_attitude", range(9, 19), "att",
     f"{INSTR} -- Part 3, attitudes toward exercise",
     [(1, "strongly disagree"), (2, "disagree"), (3, "Neither agree nor disagree"),
      (4, "agree"), (5, "strongly agree")]),
    ("abdulkader_mohamed_2022_exergame_exp", range(28, 33), "exg",
     f"{INSTR} -- Part 5, exergames experiences",
     [(0, "no"), (1, "yes")]),
]
FIXES = {"e2ugh": "enough", "2rmal": "normal", "k2w": "know",
         "I have 2 time": "I have no time"}


def load() -> pd.DataFrame:
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                name = next(n for n in z.namelist() if n.endswith(XLSX))
                with z.open(name) as fh:
                    return pd.read_excel(BytesIO(fh.read()))
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")


def fix(h: str) -> str:
    h = h.strip()
    for a, b in FIXES.items():
        h = h.replace(a, b)
    assert "2" not in h.replace("360", ""), h  # no stray "no"->"2" left
    return h


def main():
    raw = load()
    for table, cols, pfx, instrument, anchors in BLOCKS:
        rows = []
        for k, j in enumerate(cols, start=1):
            stem = fix(raw.columns[j])
            if raw.columns[j].strip() != stem:
                print(f"  fixed {pfx}_{k}: {raw.columns[j].strip()!r} -> {stem!r}")
            for resp, opt in anchors:
                rows.append({"table": table, "section_id": f"{table}_1",
                             "item": f"{pfx}_{k}", "instrument": instrument,
                             "instructions": None, "section_prompt": None,
                             "item_text": stem, "correct_response": None,
                             "option_text": opt, "resp": resp})
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        assert {r["item"] for r in rows} == set(resp["item"].astype(str)), table
        assert {float(r["resp"]) for r in rows} == set(resp["resp"].astype(float)), table
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{path.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
