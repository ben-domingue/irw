#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283772
# DOI: 10.1371/journal.pone.0283772
# Supporting Information: https://doi.org/10.1371/journal.pone.0283772.s001
#
# The raw `id` column fails uniqueness (1023 unique values over 1125
# rows); 102 ids appear twice with genuinely differing item responses (not
# exact duplicates), but no date/session/wave column exists anywhere in
# the file to confirm these are real repeated-measures waves rather than a
# data-entry issue -- per the IRW standard's guidance for a non-unique id
# column, the row index is used instead rather than guessing a wave
# structure. Raw file has 6 scales: Quality of Life (QoL, 13 items),
# Rosenberg Self-Esteem Scale (RSES, 10 items), Sense of Coherence (soc,
# 13 items), Life Satisfaction Index (LSITA, 12 items), Geriatric
# Depression Scale (gds, 15 items), Geriatric Anxiety Inventory (gai, 20
# items). A separate zs5x1-12 block (12 binary items) was not confidently
# identified as a named instrument and is not included.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0283772.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"age": "cov_age", "d1pohlavi": "cov_gender"}

SCALES = {
    "buzgova_2023_qol": [f"QoL{i}" for i in range(1, 14)],
    "buzgova_2023_rses": [f"RSES{i}" for i in range(1, 11)],
    "buzgova_2023_soc": [f"soc{i}" for i in range(1, 14)],
    "buzgova_2023_lsita": [f"LSITA{i}" for i in range(1, 13)],
    "buzgova_2023_gds": [f"gds{i}" for i in range(1, 16)],
    "buzgova_2023_gai": [f"gai{i}" for i in range(1, 21)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df = df.drop(columns=["id"]).reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
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
    cov_cols = list(COV_RENAME.values())
    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)


if __name__ == "__main__":
    convert()
