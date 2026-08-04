#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0290757
# DOI: 10.1371/journal.pone.0290757
# Supporting Information (raw data): https://doi.org/10.1371/journal.pone.0290757.s003 (S1 Dataset)
# Supporting Information (codebook): https://doi.org/10.1371/journal.pone.0290757.s002 (S2 File)
#
# Companion table to evans_2023_vaccine_hesitancy.py -- see that script's
# header comment for full background on the study (Nigeria COVID-19
# vaccination chatbot campaign, 3 waves, treat/campaign assignment,
# attrition, and imputation notes). This script produces the
# "pro-vaccination social norms" five-item scale (close/family/friends/
# healthc/nigerian), each item scored 1-5 per the S2 File codebook
# (nominally a "what proportion of people" question but coded as an
# ordinal 1-5 category, consistent with the codebook's stated response
# options). The composite `norms*` columns (row means) are excluded as
# derived/aggregate.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0290757.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

OUT_NAME = "evans_2023_vaccination_norms"

NORMS_ITEMS = ["close", "family", "friends", "healthc", "nigerian"]

COV_RENAME = {
    "gender0": "cov_gender",
    "agegrp0": "cov_agegrp",
    "edu0": "cov_edu",
    "religion0": "cov_religion",
    "empsect0": "cov_empsect",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")


def convert():
    df = fetch_data()
    df = df.rename(columns={"userid": "id"})
    df = df.rename(columns=COV_RENAME)
    assert df["id"].nunique() == len(df), "id column is not unique per respondent"

    cov_cols = list(COV_RENAME.values())

    frames = []
    for w_idx, wave in enumerate(["0", "1", "2"], start=1):
        wave_cols = [f"{item}{wave}" for item in NORMS_ITEMS]
        sub = df[["id", "treat"] + cov_cols + wave_cols].copy()
        sub = sub.rename(columns={f"{item}{wave}": item for item in NORMS_ITEMS})
        long = sub.melt(id_vars=["id", "treat"] + cov_cols, value_vars=NORMS_ITEMS,
                         var_name="item", value_name="resp")
        long["wave"] = w_idx
        frames.append(long)

    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp", "wave", "treat"] + cov_cols
    long = long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{OUT_NAME}.csv"
    long.to_csv(out_path, index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
