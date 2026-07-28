#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255039
# DOI: 10.1371/journal.pone.0255039
# Supporting Information: https://doi.org/10.1371/journal.pone.0255039.s001
#
# The raw file bundles two short scales: a 3-item phenomenology-of-imagery
# scale (pheno_detail/duration/manipulation, each 1-3) and a 7-item
# "modality used per cognitive task" scale (use_*, each 0-2). Per the IRW
# standard (one scale per file), this produces two output files. The
# `open_question` free-text column is dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0255039.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "age": "cov_age",
    "sex [1=M; 2=F]": "cov_sex",
    "education [1=BEP/CAP; 2=BAC; 3=BAC+2; 4=BAC+3; 5=BAC+5; 6=BAC+8]": "cov_education",
    "group [0=control; 1=autism]": "cov_group",
}

PHENO_COLS = ["pheno_detail [1=detailed; 2=detailed/blurry; 3=blurry]",
              "pheno_duration [1=short_dur; 2=short/persistent; 3=persistent]",
              "pheno_manipulation [1=never; 2=sometimes; 3=always]"]

IMAGERY_COLS = [
    "use_recollection [0=words_only; 1=images/words; 2=imges_only]",
    "use_comprehension [0=words_only; 1=images/words; 2=imges_only]",
    "use_anticipation [0=words_only; 1=images/words; 2=imges_only]",
    "use_planification [0=words_only; 1=images/words; 2=imges_only]",
    "use_problemSolving [0=words_only; 1=images/words; 2=imges_only]",
    "use_decision [0=words_only; 1=images/words; 2=imges_only]",
    "use_memorization [0=words_only; 1=images/words; 2=imges_only]",
]

ITEM_RENAME = {
    "pheno_detail [1=detailed; 2=detailed/blurry; 3=blurry]": "pheno_detail",
    "pheno_duration [1=short_dur; 2=short/persistent; 3=persistent]": "pheno_duration",
    "pheno_manipulation [1=never; 2=sometimes; 3=always]": "pheno_manipulation",
    "use_recollection [0=words_only; 1=images/words; 2=imges_only]": "use_recollection",
    "use_comprehension [0=words_only; 1=images/words; 2=imges_only]": "use_comprehension",
    "use_anticipation [0=words_only; 1=images/words; 2=imges_only]": "use_anticipation",
    "use_planification [0=words_only; 1=images/words; 2=imges_only]": "use_planification",
    "use_problemSolving [0=words_only; 1=images/words; 2=imges_only]": "use_problemSolving",
    "use_decision [0=words_only; 1=images/words; 2=imges_only]": "use_decision",
    "use_memorization [0=words_only; 1=images/words; 2=imges_only]": "use_memorization",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns={"id": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    return df.rename(columns=ITEM_RENAME)


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_data()
    pheno_items = [ITEM_RENAME[c] for c in PHENO_COLS]
    imagery_items = [ITEM_RENAME[c] for c in IMAGERY_COLS]
    melt_scale(df, pheno_items, "bled_2021_imagery_phenomenology.csv")
    melt_scale(df, imagery_items, "bled_2021_imagery_use.csv")


if __name__ == "__main__":
    convert()
