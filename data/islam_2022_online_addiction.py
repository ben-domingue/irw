#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0279062
# DOI: 10.1371/journal.pone.0279062
#
# Islam et al. 2022, "Psychometric properties of three online-related
# addictive behavior instruments among Bangladeshi school-going
# adolescents." Single SI file (journal.pone.0279062_S1_File.xlsx, CC BY),
# N=428, no person-ID column in the source -- row index used as id. Five
# scales in the same file, each its own instrument: IGDS9-SF (gaming
# disorder, 9 items, 1-5), GDT (gaming disorder tendencies, 4 items, 1-5),
# PHQ-9 (depression, 9 items, 0-3), GAD-7 (anxiety, 7 items, 0-3), BSMAS
# (Bergen social media addiction, 6 items, 1-5). Sum_* composite columns
# dropped -- aggregates, not raw items.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0279062.s001")

COV_COLS = {
    "Age": "cov_age",
    "Sex": "cov_sex",
    "Marital status": "cov_marital_status",
    "Academic grades": "cov_academic_grades",
    "Family type": "cov_family_type",
    "Monthly income": "cov_monthly_income",
    "Living status": "cov_living_status",
    "Hours of internet use": "cov_hours_internet_use",
    "Hours of playing game": "cov_hours_playing_game",
}

SCALES = {
    "islam_2022_igds9sf.csv": [f"IGDS9-SF{i}" for i in range(1, 10)],
    "islam_2022_gdt.csv": [f"GDT{i}" for i in range(1, 5)],
    "islam_2022_phq9.csv": [f"PHQ{i}" for i in range(1, 10)],
    "islam_2022_gad7.csv": [f"GAD{i}" for i in range(1, 8)],
    "islam_2022_bsmas.csv": [f"BSMAS{i}" for i in range(1, 7)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def build_long(df: pd.DataFrame, item_cols: list[str], cov_cols: list[str]) -> pd.DataFrame:
    long = df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    out_cols = ["id", "item", "resp"] + cov_cols
    return long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)


def convert():
    print("Downloading journal.pone.0279062_S1_File.xlsx ...")
    df = fetch_data()
    df = df.rename(columns=COV_COLS)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    cov_cols = list(COV_COLS.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for fname, item_cols in SCALES.items():
        long = build_long(df, item_cols, cov_cols)
        long.to_csv(OUT_DIR / fname, index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
