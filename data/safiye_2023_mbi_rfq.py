#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0279535
# DOI: 10.1371/journal.pone.0279535
# Supporting Information: https://doi.org/10.1371/journal.pone.0279535.s001
#
# Automated triage flagged this as low-confidence id mapping; id is
# clean/unique (823/823). Raw file has the full 22-item Maslach Burnout
# Inventory (MBI) and the 8-item Reflective Functioning Questionnaire
# (RFQ), the paper's focal "mentalizing" measure. RFQc1-6/RFQu2-8 are
# per-item transformed scores used to compute the RFQ's two subscales
# (Certainty/Uncertainty about Mental States) -- redundant with the raw
# RFQ1-8 items, not used. RFQ_c/RFQ_u and EE.Mbi/DP.Mbi/Pa.Mbi (+ their
# Mean.* twins) are subscale/mean aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0279535.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_MBI = {"Never": 0, "A few times a year or less": 1, "Once a month or less": 2,
           "A few times a month": 3, "Once a week": 4, "A few times a week": 5,
           "Every day": 6}
MAP_RFQ = {"Strongly disagree": 1, "I disagree": 2, "I partially disagree": 3,
           "I neither agree nor disagree": 4, "I partially agree": 5, "I agree": 6,
           "Strongly agree": 7}

COV_RENAME = {"Gender": "cov_gender", "Age": "cov_age", "LevelOfEducation": "cov_education",
              "MaritalStatus": "cov_marital_status", "LengthOfService": "cov_length_of_service"}

MBI_COLS = [f"MBI{i}" for i in range(1, 23)]
RFQ_COLS = [f"RFQ{i}" for i in range(1, 9)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str],
               value_map: dict, out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, MBI_COLS, MAP_MBI, "safiye_2023_mbi")
    melt_scale(df, cov_cols, RFQ_COLS, MAP_RFQ, "safiye_2023_rfq")


if __name__ == "__main__":
    convert()
