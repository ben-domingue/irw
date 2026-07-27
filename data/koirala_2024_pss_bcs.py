#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0305588
# DOI: 10.1371/journal.pone.0305588
# Supporting Information: https://doi.org/10.1371/journal.pone.0305588.s001
#
# AQ1-6/BQ1-5/CQ1-6 are demographic/background questions (age, income
# bracket, institution name, ...), not psychometric items -- excluded.
# Raw file has PSS-10 and the 28-item Brief COPE scale. Problemfocused/
# Emotionfocused/Avoidantcoping/Briefcoping/newbriefcoping and PSS_Sum1/
# Stresslevel1 are subscale/total aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0305588.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_PSS = {"Never": 0, "Almost never": 1, "Sometimes": 2, "Fairly often": 3, "Very often": 4}
MAP_BCS = {"I haven't been doing this at all": 1, "A little bit": 2,
           "A medium amount": 3, "I've been doing this alot": 4}

PSS_COLS = [f"PSS{i}" for i in range(1, 11)]
BCS_COLS = [f"BCS{i}" for i in range(1, 29)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, item_cols: list[str], value_map: dict, out_name: str):
    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"SN": "id"})
    assert df["id"].nunique() == len(df)

    melt_scale(df, PSS_COLS, MAP_PSS, "koirala_2024_pss10")
    melt_scale(df, BCS_COLS, MAP_BCS, "koirala_2024_brief_cope")


if __name__ == "__main__":
    convert()
