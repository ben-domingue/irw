#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0194559
# DOI: 10.1371/journal.pone.0194559
# Supporting Information: https://doi.org/10.1371/journal.pone.0194559.s002
#
# Raw file bundles 5 raw-item scales (life satisfaction/SWLS 5 items,
# Shyness 13 items, PANAS 20 items, General Self-Efficacy 10 items,
# Optimism/LOT-R 10 items) plus a second set of SEM item-PARCEL columns
# (shyness_1-3, LOT_R_1-3, PA_1-3, NA_1-3, GSE_1-3, LS_1-3) -- confirmed
# these are averaged composites, not items (fractional values like
# 1.333333, not achievable from any single Likert response) -- excluded.
# One output file per raw-item scale.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0194559.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Age": "cov_age_group",
    "Gender": "cov_gender",
    "Education": "cov_education",
    "Relationship_Status": "cov_relationship_status",
    "Companies": "cov_company_size_group",
    "Positions": "cov_job_position",
}

SCALES = {
    "liu_2018_swls": ["life_satisfication01", "life_satisfication02",
                       "life_satisficatio03", "life_satisficatio04",
                       "life_satisficatio05"],
    "liu_2018_shyness": [f"Shyness{i:02d}" for i in range(1, 14)],
    "liu_2018_panas": [f"PANAS{i}" for i in range(1, 21)],
    "liu_2018_gse": [f"self_efficacy{i:02d}" for i in range(1, 11)],
    "liu_2018_lot_r": [f"Optimism{i}" for i in range(1, 11)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


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
    df = df.rename(columns={"Serial_number": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)


if __name__ == "__main__":
    convert()
