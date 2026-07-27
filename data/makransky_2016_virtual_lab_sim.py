#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0155895
# DOI: 10.1371/journal.pone.0155895
# Supporting Information: https://doi.org/10.1371/journal.pone.0155895.s001
#
# Virtual-simulation lab-training study, N=189, pre/post design (same
# items asked before and after the lab exercise -- wave 1=pre, 2=post):
#   motivation -- 5-item motivation scale, 5-point agree/disagree Likert
#     (text: Completely disagree < Disagree < Neither < Agree < Completely
#     agree; "Completely disagree" never occurs in this scale specifically
#     but the label set is otherwise identical to `self_efficacy`, so kept
#     as a genuine unused category rather than assumed to be a 4-point
#     scale).
#   self_efficacy -- 8-item self-efficacy scale, same 5-point Likert.
#   mcq_correct -- 10-item multiple-choice knowledge test, binary
#     correct(1)/incorrect(0), already numeric.
# Plate_score/Pre_total_score/Post_total_score/Pre_motivation_5scale/
# Post_motivation_5scale/Pre_SE_5scale/Post_SE_5scale are aggregates,
# excluded. Raw (non-"_correct") MCQ response-option columns not
# processed here -- only the correct/incorrect scoring is a clean binary
# item; the raw option letters would need the item key to interpret.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0155895.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Group": "cov_group", "Gender": "cov_sex", "Age": "cov_age"}
MAP_LIKERT = {"Completely disagree": 1, "Disagree": 2, "Neither agree nor disagree": 3,
              "Agree": 4, "Completely agree": 5}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id", **COV_RENAME})


def melt_wave_likert(df, cov_cols, n_items, prefix, out_name):
    frames = []
    for wave, tag in [(1, "PRE"), (2, "POST")]:
        cols = [f"{tag}_{prefix}{i}" for i in range(1, n_items + 1)]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                        var_name="item", value_name="resp")
        long["item"] = long["item"].str.replace(f"{tag}_", "", regex=False)
        long["wave"] = wave
        long["resp"] = long["resp"].map(MAP_LIKERT)
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def melt_wave_correct(df, cov_cols, n_items, out_name):
    frames = []
    for wave, tag in [(1, "Pre"), (2, "Post")]:
        cols = [f"{tag}_MCQ{i}_correct" for i in range(1, n_items + 1)]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                        var_name="item", value_name="resp")
        long["item"] = long["item"].str.replace(f"{tag}_", "", regex=False)
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def save(long, cov_cols, out_name):
    long = long[["id", "item", "resp", "wave"] + cov_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_wave_likert(df, cov_cols, 5, "Mot", "makransky_2016_motivation")
    melt_wave_likert(df, cov_cols, 8, "SE", "makransky_2016_self_efficacy")
    melt_wave_correct(df, cov_cols, 10, "makransky_2016_mcq_correct")


if __name__ == "__main__":
    convert()
