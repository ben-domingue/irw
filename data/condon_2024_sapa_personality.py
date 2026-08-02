#!/usr/bin/env python3
# Source: SAPA-Project annual personality-item releases, Harvard Dataverse
# Condon, D. M., & Revelle, W. "Selected personality data from the SAPA-Project"
# 7 annual deposits, 2017-01-01 through 2024-01-12, all CC0 1.0:
#   DVN/PNGUT5 (2017), DVN/7A9YMV (2018), DVN/FUUB2Q (2019), DVN/YOEEDQ (2020),
#   DVN/JOGYUD (2021), DVN/BVF52I (2022), DVN/3BTT82 (2023-24)
#
# All 7 releases share the identical 135-item q_### personality item bank
# (confirmed by hashing headers) -- only the respondent cohort differs by
# year. Pooled here into one long-format table with cov_year, following the
# id-offset rule in datastandard.md (raw per-year ids are file-local and
# overlap across years, so composite string ids "<year>_<orig_id>" are used).
#
# Full pool is ~2.28M unique respondents / ~155.7M item-response rows --
# far larger than typical for this pipeline. Per ben-domingue's direction
# (2026-08-02), a random sample of 1,000,000 respondents (seed=42) is taken
# after pooling. Shipped as its own table, separate from (not merged into)
# the existing sapa_personality table (data/sapa-personality.R, 696-item
# pool, 2013-12-08 to 2014-07-26) -- this pooled 2017-2024 release uses
# SAPA's later fixed 135-item subset instead, over a non-overlapping later
# window, so there's no respondent or item duplication between the two.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "automated_finding" / "irw_output" / "condon_2024_sapa_personality.csv"

UA = {"User-Agent": "irw-batch/1.0 (research)"}

# (year, Dataverse file id for that year's SAPAdata CSV)
YEAR_FILES = [
    (2017, 10988792),
    (2018, 10988863),
    (2019, 10988866),
    (2020, 10988879),
    (2021, 10988881),
    (2022, 10988884),
    (2023, 10988887),
]

N_SAMPLE = 1_000_000
SEED = 42


def fetch_year(year: int, file_id: int) -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{file_id}"
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), low_memory=False)
    df = df.rename(columns={df.columns[0]: "orig_id"})
    df["id"] = df["orig_id"].astype(str) + f"_{year}"
    df["cov_year"] = year
    df = df.rename(columns={"sex": "cov_sex", "age": "cov_age", "english": "cov_english"})
    keep = ["id", "cov_year", "cov_sex", "cov_age", "cov_english"]
    item_cols = [c for c in df.columns if c.startswith("q_")]
    return df[keep + item_cols]


def build() -> pd.DataFrame:
    frames = [fetch_year(year, fid) for year, fid in YEAR_FILES]
    wide = pd.concat(frames, ignore_index=True, sort=False)
    assert wide["id"].is_unique, "composite id not unique across pooled years"

    sample_ids = wide["id"].sample(n=N_SAMPLE, random_state=SEED)
    wide = wide[wide["id"].isin(set(sample_ids))].reset_index(drop=True)

    cov_cols = ["cov_year", "cov_sex", "cov_age", "cov_english"]
    item_cols = [c for c in wide.columns if c.startswith("q_")]

    long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                      var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"] + cov_cols]
    return long


if __name__ == "__main__":
    long = build()
    long.to_csv(OUT_PATH, index=False)
    print(f"{OUT_PATH.name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()} "
          f"years={sorted(long['cov_year'].unique())}")
