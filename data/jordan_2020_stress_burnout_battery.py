#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0240667
# DOI: 10.1371/journal.pone.0240667
# Supporting Information: https://doi.org/10.1371/journal.pone.0240667.s001
#
# Qualtrics export with 3 header rows (ImportId JSON, question text, short
# variable code) above the data -- header=2 selects the short-code row.
# Automated triage found only n_items=2; real content is 4 raw-item
# scales: Q12 (10 items, Copenhagen Burnout Inventory-style frequency),
# Q13 (10 items, PSS-10 wording), Q14 (6 items, Brief Resilience Scale
# wording), Q15 (12 items, mindfulness "true" wording). A separate Q11 (3
# items) mixes two different response-label sets within the same items
# (e.g. "Often" and "To a high degree" both appear for the same column)
# with no way to tell if this reflects real survey-wording drift across
# the study's repeated administrations or a coding issue -- excluded
# rather than guessed. No person-ID column exists; row index used.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0240667.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_FREQ5 = {"Never/almost never": 0, "Seldom": 1, "Sometimes": 2, "Often": 3, "Always": 4}
MAP_PSS = {"Never": 0, "Almost Never": 1, "Sometimes": 2, "Fairly Often": 3, "Very Often": 4}
MAP_AGREE5 = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4,
              "Strongly Agree": 5}
MAP_TRUE5 = {"Never or very rarely true": 1, "Rarely true": 2, "Sometimes true": 3,
             "Often true": 4, "Very often or always true": 5}

SCALES = {
    "jordan_2020_burnout": ([f"Q12_{i}" for i in range(1, 11)], MAP_FREQ5),
    "jordan_2020_pss10": ([f"Q13_{i}" for i in range(1, 11)], MAP_PSS),
    "jordan_2020_resilience": ([f"Q14_{i}" for i in range(1, 7)], MAP_AGREE5),
    "jordan_2020_mindfulness": ([f"Q15_{i}" for i in range(1, 13)], MAP_TRUE5),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), header=2)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def melt_scale(df: pd.DataFrame, item_cols: list[str], value_map: dict, out_name: str):
    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    for out_name, (item_cols, value_map) in SCALES.items():
        melt_scale(df, item_cols, value_map, out_name)


if __name__ == "__main__":
    convert()
