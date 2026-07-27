#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247114
# DOI: 10.1371/journal.pone.0247114
# Supporting Information: S1 (N=282) https://doi.org/10.1371/journal.pone.0247114.s001
#                          S3 (N=202) https://doi.org/10.1371/journal.pone.0247114.s003
#
# The article has 4 SI files (S1-S4), one per validation (sub)study, each
# with a different subset/naming of scales -- not merged, since sample
# sizes/id spaces are independent across studies. This script uses only
# S1 (richest: 9 full scales) and S3 (the CPC-12 alone, in a different
# `cpc1-12` naming, same instrument as S1's PsyCap1-12). S2 (a sparse
# mixed subset of single items from several subscales, no full scale) and
# S4 (has the 4 psychological-capital SUBFACETS as separate 3-4-item
# blocks -- Hope/Opt/Res/SelfEff -- rather than the combined PsyCap1-12,
# needing nontrivial remapping) were judged not worth reconciling given
# the added complexity for this pass. All *TOT/PerfTOT/TaskPerf/ExtraPerf/
# CWBi/FAC*_1 columns in S1 are aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

S1_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0247114.s001")
S3_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0247114.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES_S1 = {
    "dudasova_2021_cpc12": [f"PsyCap{i}" for i in range(1, 13)],
    "dudasova_2021_engagement": [f"Eng{i}" for i in range(1, 10)],
    "dudasova_2021_job_satisfaction": ["JS1", "JS2", "JS3i"],
    "dudasova_2021_swls": [f"LifeSat{i}" for i in range(1, 6)],
    "dudasova_2021_hope": [f"Hope{i}" if i not in (3, 5, 7, 11) else f"Hope{i}i"
                            for i in range(1, 13)],
    "dudasova_2021_social_support": [f"SocSup{i}" for i in range(1, 13)],
    "dudasova_2021_gratitude": ["Grat1", "Grat2", "Grat3i", "Grat4", "Grat5", "Grat6"],
    "dudasova_2021_positive_affect": [f"PosAff{i}" for i in range(1, 12)],
    "dudasova_2021_performance": [f"Perf{i}" if i not in (14, 15, 16, 17, 18) else f"Perf{i}i"
                                   for i in range(1, 19)],
}


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    r1 = requests.get(S1_URL, headers=UA, timeout=60)
    r1.raise_for_status()
    df1 = pd.read_spss(io.BytesIO(r1.content)).rename(columns={"ID": "id"})
    assert df1["id"].nunique() == len(df1)
    for out_name, item_cols in SCALES_S1.items():
        melt_scale(df1, item_cols, out_name)

    r3 = requests.get(S3_URL, headers=UA, timeout=60)
    r3.raise_for_status()
    df3 = pd.read_spss(io.BytesIO(r3.content))
    df3 = df3.reset_index(drop=True)
    df3.insert(0, "id", df3.index + 1)
    melt_scale(df3, [f"cpc{i}" for i in range(1, 13)], "dudasova_2021_cpc12_study3")


if __name__ == "__main__":
    convert()
