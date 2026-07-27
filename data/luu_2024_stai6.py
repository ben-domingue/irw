#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280144
# DOI: 10.1371/journal.pone.0280144
# Supporting Information: https://doi.org/10.1371/journal.pone.0280144.s003
#
# Raw file has the 6-item State-Trait Anxiety Inventory short form
# (STAI-6): "I feel calm", "I am tense", "I feel upset", "I am relaxed",
# "I feel content", "I am worried", text-coded as "1. Not at all" .. "4.
# Very much" -- leading integer extracted. The STAI6 column (a computed
# total) and many other unrelated single-item survey questions in the same
# file are excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0280144.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Age group ": "cov_age_group",
    "Gender ": "cov_gender",
    "Living location ": "cov_living_location",
    "Marital status ": "cov_marital_status",
}

ITEM_COLS = ["I feel calm", "I am tense", "I feel upset", "I am relaxed",
             "I feel content", "I am worried"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for c in ITEM_COLS:
        df[c] = df[c].astype(str).str.extract(r"(\d+)").astype(float)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "luu_2024_stai6.csv", index=False)
    print(f"luu_2024_stai6.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
