#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0245964
# DOI: 10.1371/journal.pone.0245964
# Supporting Information: https://doi.org/10.1371/journal.pone.0245964.s002 (S1 Data, CSV)
#
# 5 constructs (perceived risk, perceived fairness, reward sensitivity,
# complexity, usage intention), each measured with 3 items on a 7-point
# Likert scale (1 = strongly disagree to 7 = strongly agree), assessing
# SMEs' adoption intentions for a blockchain-based loan system. No
# demographic/covariate columns are present in the SI file -- it is item
# responses only. All 15 items are clean integers 1-7 across all 296
# respondents; no sentinel/out-of-range values found.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0245964.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["pr1", "pr2", "pr3", "pf1", "pf2", "pf3", "rs1", "rs2", "rs3",
             "com1", "com2", "com3", "ui1", "ui2", "ui3"]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns={"No": "id"})
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "sun_2021_blockchain_loan_adoption.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} rows={len(long)}")


if __name__ == "__main__":
    convert()
