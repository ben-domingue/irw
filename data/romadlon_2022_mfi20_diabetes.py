#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0278165
# DOI: 10.1371/journal.pone.0278165
# Supporting Information: https://doi.org/10.1371/journal.pone.0278165.s004
#
# Type 2 diabetes patients, N=200 (142 unique `Sample` initials-codes --
# see below). Three raw-item scales:
#   mfi20 -- Multidimensional Fatigue Inventory-20 (the paper's focal
#            instrument), 20 items, 1-5.
#   facit -- FACIT-Fatigue, 13 items, 1-4.
#   bdi   -- Beck Depression Inventory, 21 items; observed range is 0-2
#            (no respondent chose the most severe "3" option on any
#            item) -- confirmed not an isolated-value artifact since it's
#            a uniform absence across the whole scale, not one item.
#
# `Sample` holds 1-3 letter codes (likely patient initials) reused across
# different respondents (different ages/sexes under the same code,
# spot-checked directly) -- not a reliable id, and initials are also
# borderline PII, so this column is dropped entirely and row index used
# as id instead.
#
# PSQI1-7 are the 7 standard Pittsburgh Sleep Quality Index *component*
# scores (0-3 each), not raw sub-questions -- treated as derived
# subscale-level scores like SF-36's domain totals elsewhere in this
# pipeline, excluded. Q1-5 (heterogeneous formats: Q1 binary, Q2
# continuous 0-16, Q3-5 ordinal 1-4) don't form one uniform scale and
# aren't identified in available source metadata, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0278165.s004")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Age": "cov_age", "Sex": "cov_sex", "Education": "cov_education",
              "MaritalStatus": "cov_marital_status", "Treatment": "cov_treatment"}

SCALES = {
    "romadlon_2022_mfi20": [f"MFI{i}" for i in range(1, 21)],
    "romadlon_2022_facit": [f"FACIT{i}" for i in range(1, 14)],
    "romadlon_2022_bdi": [f"BDI{i}" for i in range(1, 22)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df["id"] = df.index
    return df


def melt_scale(df, cov_cols, item_cols, out_name):
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

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)


if __name__ == "__main__":
    convert()
