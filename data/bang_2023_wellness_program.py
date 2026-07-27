#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0284340
# DOI: 10.1371/journal.pone.0284340
# Supporting Information: https://doi.org/10.1371/journal.pone.0284340.s004
#
# Quasi-experimental wellness program for unmarried mothers. Raw file's
# "Data dictionary" sheet confirms 5 scales: H (physical/mental health, 14
# items), D (depression, 12 items), A (anxiety, 11 items), S (self-esteem,
# 10 items), PS (parenting stress, 36 items). One output file per scale.
# `group` (1=control, 2=experimental) mapped to the standard 0/1 `treat`
# encoding. Despite the SI caption mentioning "baseline and endline
# survey", each of the 37 `no` values is unique with no wave marker --
# single timepoint per row, no `wave` column added.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0284340.s004")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "bang_2023_health": [f"H{i}" for i in range(1, 15)],
    "bang_2023_depression": [f"D{i}" for i in range(1, 13)],
    "bang_2023_anxiety": [f"A{i}" for i in range(1, 12)],
    "bang_2023_self_esteem": [f"S{i}" for i in range(1, 11)],
    "bang_2023_parenting_stress": [f"PS{i}" for i in range(1, 37)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Ploseone_Dataset")


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id", "treat", "cov_age"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "treat", "cov_age"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"no": "id", "age": "cov_age"})
    df["treat"] = (df["group"] == 2).astype(int)
    assert df["id"].nunique() == len(df)

    for out_name, item_cols in SCALES.items():
        melt_scale(df, item_cols, out_name)


if __name__ == "__main__":
    convert()
