#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0237859
# DOI: 10.1371/journal.pone.0237859
# Supporting Information: https://doi.org/10.1371/journal.pone.0237859.s003
#
# Grandchild-reported WWII trauma-history checklist (29 real event items:
# loss of parent, combat, concentration/Soviet camp, ghetto, rape, hiding
# Jews, etc. -- confirmed via SPSS variable labels, not aggregates) asked
# separately about each of the respondent's 4 grandparents:
#   mwojb  = maternal grandmother, mwojdz = maternal grandfather
#   owojb  = paternal grandmother, owojdz = paternal grandfather
# Each item is yes/no/don't know. "don't know" is not an ordinal response
# to a factual historical question (it's a non-response, not a point
# between no and yes), so it's dropped as missing; no=0, yes=1.
#
# Also includes SWLS (5 items, 1-7) and GHQ-28 (28 items, 0-3), both
# genuine raw Likert items -- SWLS/GHQ/GHQ_A-D totals and Class_1/npamh
# (latent-class-analysis outputs) are aggregates/derived, excluded.
#
# `lp` is a family/sibling-group id (shared by 2-4 respondents of
# different age/sex who each answer about their own grandparents), not a
# per-respondent id -- row index used as id instead, `lp` kept as
# cov_family.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0237859.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"lp": "cov_family", "sex": "cov_sex", "age": "cov_age",
              "education": "cov_education", "mstatus": "cov_mstatus"}
MAP_YN = {"no": 0, "yes": 1}

GRANDPARENT_SCALES = {
    "rzeszutek_2020_wwii_matgrandmother": [f"mwojb{i}" for i in range(1, 30)],
    "rzeszutek_2020_wwii_matgrandfather": [f"mwojdz{i}" for i in range(1, 30)],
    "rzeszutek_2020_wwii_patgrandmother": [f"owojb{i}" for i in range(1, 30)],
    "rzeszutek_2020_wwii_patgrandfather": [f"owojdz{i}" for i in range(1, 30)],
}
SWLS_COLS = [f"swls{i}" for i in range(1, 6)]
GHQ_COLS = [f"ghq{i}" for i in range(1, 29)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df["id"] = df.index
    return df


def melt_yn_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(MAP_YN)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def melt_numeric_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def save(long: pd.DataFrame, cov_cols: list[str], out_name: str):
    long = long[["id", "item", "resp"] + cov_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in GRANDPARENT_SCALES.items():
        melt_yn_scale(df, cov_cols, item_cols, out_name)

    melt_numeric_scale(df, cov_cols, SWLS_COLS, "rzeszutek_2020_swls")
    melt_numeric_scale(df, cov_cols, GHQ_COLS, "rzeszutek_2020_ghq28")


if __name__ == "__main__":
    convert()
