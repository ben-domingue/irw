#!/usr/bin/env python3
"""Item text for duckmayr_2023_immigration (Duck-Mayr & Montgomery 2023).

The deposit (Harvard Dataverse doi:10.7910/DVN/HXORK9, CC0 1.0) ships the raw
Qualtrics export, lucid_data.tab, whose first data row is the question wording
of each column. data/duckmayr_2023_immigration.R keeps those column names
(IMM_1 .. IMM_10) as the item codes, so each statement is tied to its code in
the same column of the same file -- no positional inference. The line breaks
in the export are wrapping artefacts and are collapsed to single spaces, as
the authors' own 04-immigration-application.R does.

The response anchors are the five strings recorded in the data, which the
table codes 0-4 in the authors' order. The battery's shared instruction is not
in the export or the deposit, so `instructions` is left blank rather than
invented. English administration, so no language / _translated columns.

Usage: python3 automated_finding/itemtext_verification/make_itemtext_duckmayr_2023.py
"""
import re
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP = HERE / "irw_output" / "duckmayr_2023_immigration.csv"
SRC = "https://dataverse.harvard.edu/api/access/datafile/6573383?format=original"
UA = {"User-Agent": "IRW-Finder/1.0"}
TABLE = "duckmayr_2023_immigration"
INSTRUMENT = ("Immigration policy statements (Duck-Mayr & Montgomery 2023, "
              "Lucid survey)")
ITEMS = [f"IMM_{i}" for i in range(1, 11)]
OPTIONS = ["Strongly disagree", "Somewhat disagree", "Neither disagree nor agree",
           "Somewhat agree", "Strongly agree"]
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp"]


def wording():
    r = requests.get(SRC, headers=UA, timeout=300)
    r.raise_for_status()
    # Only the header and the wording row are parsed; no respondent row is read.
    first = pd.read_csv(StringIO(r.text), nrows=1, usecols=ITEMS)
    return {c: re.sub(r"\s+", " ", first.at[0, c]).strip() for c in ITEMS}


def main():
    text = wording()
    rows = [{"table": TABLE, "section_id": f"{TABLE}_1", "item": code,
             "instrument": INSTRUMENT, "instructions": "", "section_prompt": "",
             "item_text": text[code], "correct_response": "",
             "option_text": opt, "resp": k}
            for code in ITEMS for k, opt in enumerate(OPTIONS)]
    out = pd.DataFrame(rows, columns=COLS)

    if RESP.exists():  # join keys must match the staged response table
        live = pd.read_csv(RESP, usecols=["item", "resp"])
        assert set(live["item"]) == set(out["item"]), "item sets differ"
        assert set(live["resp"]) <= set(out["resp"]), "unlabelled resp value"

    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / f"{TABLE}__items.csv"
    out.to_csv(path, index=False)
    print(f"{path.name}: {len(out)} rows, {out['item'].nunique()} items")


if __name__ == "__main__":
    main()
