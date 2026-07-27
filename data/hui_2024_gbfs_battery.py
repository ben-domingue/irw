#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0300064
# DOI: 10.1371/journal.pone.0300064
# Supporting Information: https://doi.org/10.1371/journal.pone.0300064.s002
#
# Raw file bundles 3 scales: General Benefit Finding Scale (28 items, the
# paper's focal instrument, Chinese validation), WHO-5 Well-Being Index (5
# items), Perceived Stress Scale-10 (10 items). One output file per scale.
# No covariate columns present in the raw file.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0300064.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "hui_2024_gbfs": [f"b{i}" for i in range(1, 29)],
    "hui_2024_who5": [f"WHO{i}" for i in range(1, 6)],
    "hui_2024_pss10": [f"pss{i}" for i in range(1, 11)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"No": "id"})
    assert df["id"].nunique() == len(df)

    for out_name, item_cols in SCALES.items():
        melt_scale(df, item_cols, out_name)


if __name__ == "__main__":
    convert()
