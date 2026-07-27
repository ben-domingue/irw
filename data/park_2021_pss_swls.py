#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0246887
# DOI: 10.1371/journal.pone.0246887
# Supporting Information: https://doi.org/10.1371/journal.pone.0246887.s001
#
# Only 2 raw-item scales in this file (Perceived Stress Scale-10 and
# SWLS); everything else (LIB_total, QOL_*, LE_*, H_*, stress_posi/nega,
# lifesatis_sum/aver) is a _sum/_aver aggregate composite, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0246887.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"age": "cov_age", "sex": "cov_sex", "edu": "cov_education"}
STRESS_COLS = [f"stress_{i}" for i in range(1, 11)]
LIFESAT_COLS = [f"lifesatis_{i}" for i in range(1, 6)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"id_after_mahala": "id", **COV_RENAME})


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, STRESS_COLS, "park_2021_pss10")
    melt_scale(df, cov_cols, LIFESAT_COLS, "park_2021_swls")


if __name__ == "__main__":
    convert()
