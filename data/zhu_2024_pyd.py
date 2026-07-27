#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0303531
# DOI: 10.1371/journal.pone.0303531
# Supporting Information: https://doi.org/10.1371/journal.pone.0303531.s001
#
# Two-wave design: A1-A41 are the 41-item Positive Youth Development Scale
# at wave 1, SA1-SA41 the same 41 items re-administered at wave 2 (WAVE1/
# WAVE2 flags confirm this -- SA1==999 whenever WAVE2==0, matching A1's
# relationship to WAVE1). Item labels are kept as A1..A41 across both
# waves (not renamed per-wave), since this is one wave-indexed scale, not
# 82 distinct items -- duplicate id+item pairs are expected with `wave`
# present, per the IRW standard.
#
# B1-B3 / SB1-B3 are excluded: confirmed NOT raw items -- each takes only
# 7 possible values, evenly spaced by exactly 5/6 from 1 to 6 (consistent
# with an IRT-scaled theta score computed from a 3-item, 0-2-scored
# subtest, not a directly observed response), identically across all 6
# columns. 999 is used throughout as a missing-value sentinel (confirmed
# against the WAVE1/WAVE2 participation flags) and filtered out.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0303531.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_LABELS = [f"A{i}" for i in range(1, 42)]
WAVE1_COLS = [f"A{i}" for i in range(1, 42)]
WAVE2_COLS = [f"SA{i}" for i in range(1, 42)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"NO": "id", "gender": "cov_gender", "age_w1": "cov_age_w1"})
    df.loc[df["cov_gender"] == 999, "cov_gender"] = float("nan")
    df.loc[df["cov_age_w1"] == 999, "cov_age_w1"] = float("nan")
    return df


def melt_wave(df: pd.DataFrame, item_cols: list[str], wave: int) -> pd.DataFrame:
    long = df.melt(id_vars=["id", "cov_gender", "cov_age_w1"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("^SA", "A", regex=True)
    long["wave"] = wave
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long.loc[long["resp"] == 999, "resp"] = float("nan")
    return long.dropna(subset=["resp"]).reset_index(drop=True)


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)

    long1 = melt_wave(df, WAVE1_COLS, wave=1)
    long2 = melt_wave(df, WAVE2_COLS, wave=2)
    long = pd.concat([long1, long2], ignore_index=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "cov_gender", "cov_age_w1"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "zhu_2024_pyd.csv", index=False)
    print(f"zhu_2024_pyd.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} waves={sorted(long['wave'].unique())} "
          f"rows={len(long)}")


if __name__ == "__main__":
    convert()
