#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0313043
# DOI: 10.1371/journal.pone.0313043
# Supporting Information: https://doi.org/10.1371/journal.pone.0313043.s001
#
# Two scales: a1-18 (18-item ageism scale, the paper's focal instrument)
# and b1-22 (22-item Maslach Burnout Inventory). Several b-items have a
# "역산" (Korean: "reverse-calculated") twin column immediately after
# them in the raw file (b4/b4역산, b7/b7역산, etc.) -- the reverse-coded
# twin is used at that item's position in the 22-item sequence, its raw
# un-recoded counterpart skipped, matching the pattern used for wurm_2016
# in this same pass. One row with a missing 번호 (id) dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0313043.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Sex": "cov_sex", "Age": "cov_age", "Edu": "cov_education", "Mar": "cov_marital_status"}

A_COLS = [f"a{i}" for i in range(1, 19)]
REVERSED_B = {4, 7, 9, 12, 17, 18, 19, 21}
B_COLS = [f"b{i}역산" if i in REVERSED_B else f"b{i}" for i in range(1, 23)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"번호": "id", **COV_RENAME})
    df = df.dropna(subset=["id"])
    # One id (43) appears twice; disambiguate rather than drop either row.
    dup_n = df.groupby("id").cumcount()
    df["id"] = df["id"].astype(int).astype(str) + dup_n.map({0: "", 1: "-b"}).fillna("")
    return df


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    if out_name == "park_2024_ageism":
        # The ageism scale is 1-4 throughout; a single "5" on a18 (1 of
        # ~331 responses, every other item capping at 4) is a data-entry
        # error, not a real 5th category.
        long.loc[long["resp"] == 5, "resp"] = float("nan")
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

    melt_scale(df, cov_cols, A_COLS, "park_2024_ageism")
    melt_scale(df, cov_cols, B_COLS, "park_2024_mbi")


if __name__ == "__main__":
    convert()
