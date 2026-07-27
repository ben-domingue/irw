#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0164630
# DOI: 10.1371/journal.pone.0164630
# Supporting Information: https://doi.org/10.1371/journal.pone.0164630.s001
#
# Raw file bundles 4 distinct validated scales administered together to a
# Japanese sample: Disgust Propensity and Sensitivity Scale-Revised (16
# items, the paper's focal instrument), Padua Inventory (60 items, OCD
# symptoms), Anxiety Sensitivity Index (16 items), State-Trait Anxiety
# Inventory - Trait form (20 items). One output file per scale.
# S2/S3 Supporting Information files are the item *text* (Japanese/English
# wording), not data -- not used here.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0164630.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"sex": "cov_sex", "age": "cov_age"}

SCALES = {
    "iwasa_2016_dpssr": [f"dpss{i:02d}" for i in range(1, 17)],
    "iwasa_2016_padua_inventory": [f"pi{i:02d}" for i in range(1, 61)],
    "iwasa_2016_asi": [f"asi{i:02d}" for i in range(1, 17)],
    "iwasa_2016_stai_trait": [f"stai-t{i:02d}" for i in range(1, 21)],
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
    df = df.rename(columns=COV_RENAME)
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)


if __name__ == "__main__":
    convert()
