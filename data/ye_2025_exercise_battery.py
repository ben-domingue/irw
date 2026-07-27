#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0325835
# DOI: 10.1371/journal.pone.0325835
# Supporting Information: https://doi.org/10.1371/journal.pone.0325835.s001
#
# Automated triage flagged dup_id_item; confirmed the 124 duplicated
# `index` rows are exact full-row duplicates (double-submitted survey
# responses, not repeated-measures waves) -- deduplicated by keeping the
# first occurrence per index. Raw file has 3 Chinese text-coded item
# matrices (Q15_Row1-9, Q25_Row1-10, Q32_Row1-13); paper studies self-
# efficacy and health literacy as mediators of exercise->life-satisfaction,
# but item counts/wording weren't cross-checked against the full paper
# text to confirm exact instrument identity -- labeled by source question
# block rather than guessing a specific named scale.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0325835.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Ordinal direction inferred from label semantics (low->high), not
# confirmed against a published scoring key.
MAP_Q15 = {"非常困难": 1, "困难": 2, "简单": 3, "非常简单": 4}          # very difficult..very easy
MAP_Q25 = {"不符合": 1, "有点不符合": 2, "符合": 3, "非常符合": 4}       # does not fit..fits very well
MAP_Q32 = {"绝对不符合": 1, "不符合": 2, "似乎不太符合": 3, "我不确定": 4,
           "似乎符合": 5, "符合": 6, "绝对符合": 7}

COV_RENAME = {}  # source demographic columns (Q3/Q6/Q7/...) not confidently labeled; omitted

SCALES = {
    "ye_2025_q15_scale": ([f"Q15_Row{i}" for i in range(1, 10)], MAP_Q15),
    "ye_2025_q25_scale": ([f"Q25_Row{i}" for i in range(1, 11)], MAP_Q25),
    "ye_2025_q32_scale": ([f"Q32_Row{i}" for i in range(1, 14)], MAP_Q32),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"index": "id"})
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "id"] + ["id"])
    df = df.drop_duplicates(subset="id", keep="first")
    return df


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
    assert df["id"].nunique() == len(df)

    for out_name, (item_cols, value_map) in SCALES.items():
        melt_scale(df, item_cols, value_map, out_name)


if __name__ == "__main__":
    convert()
