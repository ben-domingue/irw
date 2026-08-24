"""Ren et al. (2024), Scientific Reports -- rural Chinese older adults.

Source: https://www.nature.com/articles/s41598-024-65095-0
DOI: 10.1038/s41598-024-65095-0
Data: Supplementary file 41598_2024_65095_MOESM3_ESM.xlsx (sheet "Data")
License: CC BY 4.0

N = 1,587 rural older adults (mean age 73.63). The supplement ships raw
item-level responses for four instruments alongside the composites the paper
analysed; only the items are exported here.

Tables written
--------------
ren_2024_psqi          13 sleep-disturbance/quality items (c65b-c65j, c66-c69), 1-4
ren_2024_adl           10 Barthel Index ADL items, weighted 0/5/10/15
ren_2024_phq9           9 PHQ-9 items, 1-4
ren_2024_loneliness     3 UCLA three-item loneliness items, 1-3
ren_2024_eq5d           5 EQ-5D-3L dimension items, recoded 1-3 (see below)

Deliberately excluded
---------------------
c61_1-c64_1   PSQI open-ended items (bedtime, sleep latency in minutes, sleep
              duration in hours, wake time) and c65a, which is continuous on the
              same scale -- these are not ordinal item responses.
SleepQuality1-7  PSQI *component* scores (0-3), each derived from the raw items
              above; composites, not responses.
PSQI, ADL, Depressive, Loneliness, EQ5D  scale totals / utility index.
Z*            standardised versions of those totals.

EQ-5D note: the deposit stores each of the five dimensions as its country-tariff
utility decrement rather than the 1/2/3 severity level (e.g. UM in
{0, 0.0766, 0.2668}). Each dimension has exactly three distinct, strictly
ordered values, so the level is recovered exactly by ranking them -- 1 = no
problems (decrement 0) through 3 = extreme problems. The paper documents the
instrument as "EQ-5D-3L: 5 dimensions with 3 severity levels".
"""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.1038/s41598-024-65095-0"
SRC = ("https://static-content.springer.com/esm/"
       "art%3A10.1038%2Fs41598-024-65095-0/MediaObjects/"
       "41598_2024_65095_MOESM3_ESM.xlsx")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PSQI_ITEMS = [f"c65{c}" for c in "bcdefghij"] + ["c66", "c67", "c68", "c69"]
ADL_ITEMS = ["Feeding", "Bathing", "Grooming", "Dressing", "BowelControl",
             "BladderControl", "ToiletUse", "Transfer", "Mobility",
             "StairClimbing"]
PHQ9_ITEMS = [f"P{i}" for i in range(1, 10)]
LONELY_ITEMS = ["L1", "L2", "L3"]
EQ5D_ITEMS = ["UM", "US", "UUA", "UP", "UAD"]

COV_MAP = {
    "Gender": "cov_gender",
    "Age": "cov_age_group",
    "MaritalStatus": "cov_marital_status",
    "Education": "cov_education",
    "INCOME": "cov_income",
    "CHRONIC1": "cov_n_chronic_conditions",
    "CHRONIC2": "cov_chronic_condition_group",
    "Drinking": "cov_drinking",
    "Smoking": "cov_smoking",
    "Regularexercise": "cov_regular_exercise",
}

SCALES = [
    ("ren_2024_psqi", PSQI_ITEMS, (1, 4)),
    ("ren_2024_adl", ADL_ITEMS, (0, 15)),
    ("ren_2024_phq9", PHQ9_ITEMS, (1, 4)),
    ("ren_2024_loneliness", LONELY_ITEMS, (1, 3)),
    ("ren_2024_eq5d", EQ5D_ITEMS, (1, 3)),
]


def fetch() -> pd.DataFrame:
    r = requests.get(SRC, headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Data")


def recode_eq5d(df: pd.DataFrame) -> pd.DataFrame:
    """Utility decrements -> 1/2/3 severity levels, per dimension."""
    df = df.copy()
    for col in EQ5D_ITEMS:
        levels = sorted(df[col].dropna().unique())
        if len(levels) != 3:
            raise ValueError(f"{col}: expected 3 distinct decrements, got {levels}")
        df[col] = df[col].map({v: i + 1 for i, v in enumerate(levels)})
    return df


def make_scale(df: pd.DataFrame, items: list[str], bounds: tuple[int, int]) -> pd.DataFrame:
    cov_cols = list(COV_MAP.values())
    long = df[["id"] + cov_cols + items].melt(
        id_vars=["id"] + cov_cols,
        value_vars=items,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    lo, hi = bounds
    long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
    long["resp"] = long["resp"].astype(int)
    return (long[["id", "item", "resp"] + cov_cols]
            .sort_values(["id", "item"])
            .reset_index(drop=True))


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = fetch()

    if raw["NowCode"].nunique() != len(raw):
        raise ValueError("NowCode is not unique per respondent")
    df = raw.rename(columns={"NowCode": "id", **COV_MAP})
    df = recode_eq5d(df)

    for name, items, bounds in SCALES:
        long = make_scale(df, items, bounds)
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
