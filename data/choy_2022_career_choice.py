#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0279411
# DOI: 10.1371/journal.pone.0279411
# Supporting Information: https://doi.org/10.1371/journal.pone.0279411.s001 (S1 Data)
#
# Bilingual (English-Chinese) survey of 407 Hong Kong tourism/hospitality
# students on career-choice motivation during the "triple-whammy" crisis
# (COVID-19, social unrest, US-China trade tension). Five 6-point Likert
# scales (1=Disagree strongly ... 6=Agree strongly, per the Methods
# section), 17 items total, cleanly prefixed in the raw file: Affect (3),
# Extraneous Events (4), Intent to Join Career (3), Lifelong Career Choice
# (3), Resilience in Workforce (4). Each scale is written as its own
# table per datastandard.md's "one file per scale" rule. The raw file
# uses -999 as a missing-value sentinel on every item column (5-45 per
# item); these are numerically in a plausible spot but confirmed as
# sentinels, not real responses, and filtered out.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0279411.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "choy_2022_affect": ["Affect1", "Affect2", "Affect3"],
    "choy_2022_extraneous_events": ["Extraneous1", "Extraneous2", "Extraneous3", "Extraneous4"],
    "choy_2022_intent_career": ["Intent1", "Intent2", "Intent3"],
    "choy_2022_lifelong_career": ["Lifelong1", "Lifelong2", "Lifelong3"],
    "choy_2022_resilience": ["Resilience1", "Resilience2", "Resilience3", "Resilience4"],
}

COV_RENAME = {
    "gender": "cov_gender",
    "age": "cov_age",
    "program": "cov_program",
    "hotel": "cov_hotel_discipline",
}

MISSING_SENTINEL = -999


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="HKG student data for PLOS ONE")


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"] != MISSING_SENTINEL]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns=COV_RENAME)
    assert df["id"].nunique() == len(df), "id column is not unique per respondent"

    cov_cols = list(COV_RENAME.values())
    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)


if __name__ == "__main__":
    convert()
