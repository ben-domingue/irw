#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0338480
# DOI: 10.1371/journal.pone.0338480
# Supporting Information: https://doi.org/10.1371/journal.pone.0338480.s001
#
# Medication-adherence questionnaire (6 items, 1-4 ordinal), pre/post
# LNG-IUD insertion, N=142. `Case` has one duplicate value (id 90 used
# twice across 144 rows for 142 respondents) -- row index used as id
# instead. SF-36 columns are subscale domain scores (not raw items) and
# Beck Depression is total-score only; both excluded, no raw items
# available for either in this file.

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0338480.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PRE_COLS = [f"pre-LNG-IUD MMAS questionnaire -{i}." for i in range(1, 7)]
POST_COLS = [f"post-LNG-IUD MMAS questionnaire -{i}." for i in range(1, 6)] + \
            ["postmirena-LNG-IUD MMAS questionnaire -6."]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df["id"] = df.index
    return df


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)

    frames = []
    for wave, cols in [(1, PRE_COLS), (2, POST_COLS)]:
        long = df.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
        long["item"] = np.repeat([f"mmas{i}" for i in range(1, 7)], len(df))
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "kolcu_2025_mmas.csv", index=False)
    print(f"kolcu_2025_mmas.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
