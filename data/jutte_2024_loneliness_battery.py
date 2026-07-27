#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296423
# DOI: 10.1371/journal.pone.0296423
# Supporting Information: https://doi.org/10.1371/journal.pone.0296423.s003
#
# 2-wave panel during COVID-era restrictions on face-to-face contact.
# 3-item short Loneliness Scale administered at both waves (explicit
# _w1/_w2 suffixes) -- kept as one table with a wave column. Single-item
# Big Five domain ratings (Extraversion_w2 etc.) administered once (wave
# 2 only) -- kept as a second table, no wave column. SM_Total/OtherMedia_
# Total/*_change/*_MOD columns are derived composite/interaction terms,
# excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0296423.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Age": "cov_age", "Female": "cov_female", "Education": "cov_education"}

LON_ITEMS = ["Loneliness_I1", "Loneliness_I2", "Loneliness_I3"]
PERSONALITY_COLS = ["Extraversion_w2", "Agreeableness_w2", "Conscientiousness_w2",
                     "Neuroticism_w2", "Openness_w2"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"responseid_2020_1": "id", **COV_RENAME})


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    frames = []
    for wave, suffix in [(1, "_w1"), (2, "_w2")]:
        cols = [f"{item}{suffix}" for item in LON_ITEMS]
        sub = df[["id"] + cov_cols + cols].copy()
        sub = sub.rename(columns=dict(zip(cols, LON_ITEMS)))
        sub["wave"] = wave
        frames.append(sub)
    lon = pd.concat(frames, ignore_index=True)
    long = lon.melt(id_vars=["id", "wave"] + cov_cols, value_vars=LON_ITEMS,
                     var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + cov_cols]
    long.to_csv(OUT_DIR / "jutte_2024_loneliness.csv", index=False)
    print(f"jutte_2024_loneliness.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()} "
          f"waves={sorted(long['wave'].unique())}")

    long2 = df.melt(id_vars=["id"] + cov_cols, value_vars=PERSONALITY_COLS,
                     var_name="item", value_name="resp")
    long2["resp"] = pd.to_numeric(long2["resp"], errors="coerce")
    long2 = long2.dropna(subset=["resp"]).reset_index(drop=True)
    long2["resp"] = long2["resp"].astype(int)
    long2 = long2[["id", "item", "resp"] + cov_cols]
    long2.to_csv(OUT_DIR / "jutte_2024_personality.csv", index=False)
    print(f"jutte_2024_personality.csv: ids={long2['id'].nunique()} "
          f"items={long2['item'].nunique()} resp={long2['resp'].min()}-{long2['resp'].max()}")


if __name__ == "__main__":
    convert()
