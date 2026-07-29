#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0250424
# DOI: 10.1371/journal.pone.0250424
# Supporting Information: https://doi.org/10.1371/journal.pone.0250424.s001
#
# First 10 raw Strengths and Difficulties Questionnaire (SDQ) items, 0-2
# scale, from a survey of school-going adolescents in Ghana. SDQ_TOTAL,
# PROSOCIAL/EMOTIONAL/CONDUCT/HYPERACTIVITY/PEER (subscale totals),
# TOTAL_DF_old, and the SDQ*_CAT columns (banded/categorized recodes of
# the full 25-item SDQ, not raw responses to SDQ_1-10) are all derived
# and excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0250424.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"SDQ_{i}" for i in range(1, 11)]
COV_RENAME = {"Location": "cov_location", "age": "cov_age", "sex": "cov_sex",
              "status": "cov_status", "religion": "cov_religion"}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content), convert_categoricals=False)
    df = df.rename(columns={"questionnaire_no": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 2)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "addy_2021_sdq_ghana.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
