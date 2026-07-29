#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0333086
# DOI: 10.1371/journal.pone.0333086
# Supporting Information: https://doi.org/10.1371/journal.pone.0333086.s001
#
# 19-item single-file survey (each item a 1-5 Likert rating of a distinct
# health-behaviour-related construct -- health attitude, knowledge, social
# support, etc.); paper reports Cronbach's alpha=0.889 across the full set,
# so treated as one instrument rather than 19 separate single-item scales.
# The raw file's extra "Age" column (values 1-5, inconsistent with the
# "2. What is your age?" column) could not be verified against a codebook
# and is dropped rather than guessed at.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0333086.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "1. What is your gender?": "cov_gender",
    "2. What is your age?": "cov_age_bracket",
    "3.What is your current level of education?": "cov_education",
    "4.What is your current academic year?": "cov_academic_year",
}
DROP_COLS = ["Age"]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"Serial number": "id", **COV_RENAME})
    df = df.drop(columns=DROP_COLS)
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    cov_cols = list(COV_RENAME.values())
    item_cols = [c for c in df.columns if c not in ["id"] + cov_cols]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "su_2025_health_behaviors.csv"
    long.to_csv(out_path, index=False)
    print(f"su_2025_health_behaviors: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
