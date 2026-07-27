#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0275292
# DOI: 10.1371/journal.pone.0275292
# Supporting Information: https://doi.org/10.1371/journal.pone.0275292.s001
#
# The raw file bundles a GAD-7 anxiety battery and a separate 13-item
# "how important is X to you" values battery in one sheet, plus free-text
# and single-item questions. Per the IRW standard (one scale per file),
# this produces two output files: this values-importance one and
# yin_2022_gad7.py. No person-ID column exists in the raw file, so the
# row index is used.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0275292.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Learning type": "cov_learning_type",
    "grade": "cov_grade",
    "gender": "cov_gender",
    "race ethnicity": "cov_race_ethnicity",
    "race categories": "cov_race_category",
    "vaccine status": "cov_vaccine_status",
}

VALUES_COLS = [
    "How important is having friends/socializing",
    "How important is your friends perception of you",
    "How important is making your parents proud",
    "How important is maintaining family relations",
    "How important is good health (not getting covid)",
    "How important is feeling safe",
    "How important is getting good grades",
    "How important is finishing high school ",
    "How important is going to college",
    "How important is fame",
    "How important is having adventure",
    "How important is money/wealth",
    "How important is having your own family",
]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df.rename(columns=COV_RENAME)


def convert():
    df = fetch_data()
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=VALUES_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "yin_2022_values_importance.csv"
    long.to_csv(out_path, index=False)
    print(f"yin_2022_values_importance.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
