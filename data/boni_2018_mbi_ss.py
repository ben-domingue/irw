#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0191746
# DOI: 10.1371/journal.pone.0191746
# Supporting Information: https://doi.org/10.1371/journal.pone.0191746.s005
#
# Maslach Burnout Inventory - Student Survey (MBI-SS, 15 items, 0-6 scale)
# among Brazilian medical students. 99 is a consistent missing-value
# sentinel (11-16 occurrences per item) -- filtered. The raw file also has
# 3 MBI subscale SUM/mean columns (MBI_SS_Emotional_Exhaustion, _Cynicism,
# _Academic_Efficacy) and 2 derived burnout-classification flags
# (burnout_two, burnout_three) -- aggregates, excluded. Many other columns
# are single, topically unrelated survey questions (not a coherent
# multi-item scale) -- kept only a small covariate subset.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0191746.s005")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Gender": "cov_gender",
    "Total_Family_income": "cov_family_income",
    "Self_perception_of_health": "cov_self_perceived_health",
}

ITEM_COLS = [f"MBI_{i:02d}" for i in range(1, 16)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())
    for c in cov_cols:
        df.loc[df[c] == 99, c] = float("nan")

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long.loc[long["resp"] == 99, "resp"] = float("nan")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "boni_2018_mbi_ss.csv", index=False)
    print(f"boni_2018_mbi_ss.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
