#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0245662
# DOI: 10.1371/journal.pone.0245662
# Supporting Information: https://doi.org/10.1371/journal.pone.0245662.s005

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0245662.s005")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Row 0 of the raw sheet groups C1-C17 into 4 dimensions of an individual
# earthquake-resilience scale; row 1 has the item codes themselves.
DIMENSION_MAP = {
    **{f"C{i}": "health_status" for i in range(1, 4)},
    **{f"C{i}": "mental_resilience" for i in range(4, 9)},
    **{f"C{i}": "social_adaptation" for i in range(9, 14)},
    **{f"C{i}": "disaster_response_capacity" for i in range(14, 18)},
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), header=None)
    data = raw.iloc[2:].reset_index(drop=True)
    data.columns = ["id"] + [f"C{i}" for i in range(1, 18)]
    return data.apply(pd.to_numeric, errors="coerce")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    item_cols = [f"C{i}" for i in range(1, 18)]

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    # The scale is 1-5 throughout; a small number of 0s (1-2 per item, vs.
    # hundreds at every value 1-5) are data-entry errors, not a real
    # response option -- drop them rather than keep them as valid.
    long.loc[long["resp"] == 0, "resp"] = float("nan")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long["itemcov_dimension"] = long["item"].map(DIMENSION_MAP)

    long = long[["id", "item", "resp", "itemcov_dimension"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "jiang_2021_resilience.csv"
    long.to_csv(out_path, index=False)
    print(f"jiang_2021_resilience.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
