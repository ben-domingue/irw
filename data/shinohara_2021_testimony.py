#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0261075
# DOI: 10.1371/journal.pone.0261075
#
# "The impact of positive and negative testimony on children's attitudes
# toward others". S2 Table (.s002, CSV) is the raw per-child data (N=128,
# 5- and 7-year-olds). Nine measures are used as items: reward-allocation
# ranks (allo_*, anti_*; 1-3, higher = larger reward given) and an explicit
# evaluation rating (eva_*; -2 to +2) toward puppets after first-hand
# observation, positive/negative testimony, or neutral testimony. `Age`,
# `Gender`, `Condition`, `Video Number`, `First task` are covariates. No PII.
# CC BY 4.0.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0261075.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Condition": "cov_condition",
    "Video Number": "cov_video_number",
    "First task": "cov_first_task",
}

ITEM_COLS = [
    "allo_observation", "allo_valence testimony", "allo_neutral testimony",
    "anti_observation", "anti_valence testimony", "anti_neutral testimony",
    "eva_observation", "eva_valence testimony", "eva_neutral testimony",
]


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df[["ID"] + list(COV_COLS.keys()) + ITEM_COLS].copy()
    df = df.rename(columns={"ID": "id"})
    df = df.rename(columns=COV_COLS)
    cov_cols = list(COV_COLS.values())

    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per row"

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "shinohara_2021_testimony.csv")
    long.to_csv(out_path, index=False)
    print(f"shinohara_2021_testimony: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
