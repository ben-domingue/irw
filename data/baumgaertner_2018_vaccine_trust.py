#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0191728
# DOI: 10.1371/journal.pone.0191728
# Supporting Information: https://doi.org/10.1371/journal.pone.0191728.s001
#
# Two 3-item batteries about vaccination willingness (Q66_*, Q74_*), stored
# as ordered-categorical text ("Very unlikely" ... "Very likely"), recoded
# to 1-5. The "vac_beliefs" column is a derived composite score, not a raw
# item, and is dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0191728.s005")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {"Very unlikely": 1, "Unlikely": 2, "Neither likely nor unlikely": 3,
              "Likely": 4, "Very likely": 5}

COV_RENAME = {"gender": "cov_gender", "education": "cov_education",
              "income": "cov_income", "ideology": "cov_ideology",
              "caucasian": "cov_caucasian", "age": "cov_age"}

ITEM_COLS = ["Q66_1", "Q66_2", "Q66_3", "Q74_1", "Q74_2", "Q74_3"]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_stata(io.BytesIO(r.content))
    df = df.rename(columns={"respondent_id": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    for c in ITEM_COLS:
        df[c] = df[c].astype(str).map(LIKERT_MAP)

    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "baumgaertner_2018_vaccine_trust.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
