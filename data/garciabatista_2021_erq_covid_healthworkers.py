#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259013
# DOI: 10.1371/journal.pone.0259013
# Supporting Information: https://doi.org/10.1371/journal.pone.0259013.s002
#
# Emotional Regulation Questionnaire (ERQ, 10 items, 1-5) among health
# workers during COVID-19, N=187. The PSS1-14 columns the paper's title
# implies are entirely empty in this export (0 non-null values across all
# 14 -- confirmed, not a parsing issue) so only ERQ is usable. No reliable
# id column: `TimeStamp` has only 9 unique values across 187 rows; row
# index used instead. `Email` (real PII) dropped entirely, not kept even
# as a covariate. CHPC/CPCD/ESC are single per-respondent composite scores
# (not repeated items), kept as covariates.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0259013.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Age": "cov_age", "Gender": "cov_sex", "MartialStatus": "cov_marital_status",
              "Ocupation": "cov_occupation", "Rank": "cov_rank", "Center": "cov_center",
              "City": "cov_city", "CHPC": "cov_chpc", "CPCD": "cov_cpcd", "ESC": "cov_esc"}
ITEM_COLS = [f"ERQ{i}" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df["id"] = df.index
    return df


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "garciabatista_2021_erq.csv", index=False)
    print(f"garciabatista_2021_erq.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
