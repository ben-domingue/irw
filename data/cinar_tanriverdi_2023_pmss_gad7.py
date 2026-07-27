#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288769
# DOI: 10.1371/journal.pone.0288769
# Supporting Information: https://doi.org/10.1371/journal.pone.0288769.s001 (main, N=572)
#                          https://doi.org/10.1371/journal.pone.0288769.s002 (retest, N=70)
#
# S2 is a test-retest reliability subsample of S1 (69 of 70 ids overlap,
# confirmed) -- combined into one table per scale with wave=1 (main)/2
# (retest), same pattern as lu_2017 in this same pass. S1's item columns
# also contain SPSS multiple-imputation artifacts: exactly 28 of 572 rows
# have near-integer jittered floats (e.g. 1.988282041) instead of clean
# {0,1,2,3,4} values, identically across every item -- these are imputed
# values, not real responses, and are dropped per the IRW standard
# ("remove imputed values"), not rounded. Raw file has the 13-item
# Perceived Medical School Stress scale (the paper's focal instrument,
# Q1-13) and GAD-7 (comparator instrument).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

S1_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0288769.s001")
S2_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0288769.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PMSS_COLS = [f"Q{i}" for i in range(1, 14)]
GAD_COLS = [f"GAD{i}" for i in range(1, 8)]
RETEST_PMSS_COLS = [f"RQ{i}" for i in range(1, 14)]


def fetch_main() -> pd.DataFrame:
    r = requests.get(S1_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df["wave"] = 1
    return df


def fetch_retest() -> pd.DataFrame:
    r = requests.get(S2_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    # S2 has both the original Q1-13 (first-administration values, already
    # covered by S1's wave-1 data) and RQ1-13 (the actual retest) -- drop
    # the former before renaming RQ->Q to avoid a duplicate column name.
    df = df.drop(columns=PMSS_COLS).rename(columns=dict(zip(RETEST_PMSS_COLS, PMSS_COLS)))
    df["wave"] = 2
    return df


def drop_imputed(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    clean = (df[item_cols] == df[item_cols].round()).all(axis=1)
    return df[clean].copy()


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id", "wave"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} waves={sorted(long['wave'].unique())}")


def convert():
    main = fetch_main()
    main = drop_imputed(main, PMSS_COLS + GAD_COLS)
    retest = fetch_retest()

    combined_pmss = pd.concat([main[["id", "wave"] + PMSS_COLS],
                                retest[["id", "wave"] + PMSS_COLS]], ignore_index=True)
    melt_scale(combined_pmss, PMSS_COLS, "cinar_tanriverdi_2023_pmss")
    melt_scale(main[["id", "wave"] + GAD_COLS], GAD_COLS, "cinar_tanriverdi_2023_gad7")


if __name__ == "__main__":
    convert()
