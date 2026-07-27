#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0246434
# DOI: 10.1371/journal.pone.0246434
# Supporting Information: https://doi.org/10.1371/journal.pone.0246434.s003
#
# Cognitive Fusion Questionnaire-7 (CFQ-7, the paper's focal instrument),
# clinical + non-clinical samples pooled (Population 1/2). ID is unique
# within Population 2 but has one collision within Population 1 (id 23,
# two rows with genuinely different item responses -- a duplicate-code
# data-entry issue, not an exact duplicate); Population-ID composite used
# as id, with a suffix to disambiguate that one collision. CFQ_THETA (IRT
# score), CAQ_TOT, SWLS, BDI are aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0246434.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"CFQ{i}" for i in range(1, 8)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df["cov_population"] = df["Population"].map({1.0: "clinical", 2.0: "non_clinical"})
    df["id"] = (df["Population"].astype(int).astype(str) + "-" +
                df["ID"].astype(int).astype(str))
    dup_n = df.groupby("id").cumcount()
    df["id"] = df["id"] + dup_n.map({0: "", 1: "-b"}).fillna("")
    return df


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id", "cov_population"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cov_population"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "donati_2021_cfq7.csv", index=False)
    print(f"donati_2021_cfq7.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
