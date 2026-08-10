#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0275880
# DOI: 10.1371/journal.pone.0275880
#
# DeCamp et al. (2022) "Development of a self-report instrument for
# measuring online teaching practices and discussion facilitation." PLOS
# ONE. License: CC BY 4.0.
#
# S1 Data ("Minimal dataset", SAV, N=251 instructors) has raw item-level
# responses for the 12 Likert-type items measuring frequency of specific
# instructor discussion-facilitation contribution types (Disc11_1-12,
# 1-5 scale). A8 and Disc1 are single dichotomous screening items (not part
# of the multi-item scale) and are excluded.

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0275880.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Female": "cov_female",
    "racialminority": "cov_racial_minority",
    "numberstudents": "cov_num_students",
    "timestaught": "cov_times_taught",
    "yearsteaching": "cov_years_teaching",
    "yearsonline": "cov_years_online",
    "tenuretrack": "cov_tenure_track",
    "contingent": "cov_contingent",
}

ITEM_COLS = [f"Disc11_{i}" for i in range(1, 13)]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_decamp_2022.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp)
    return df


def convert():
    print("Fetching S1 Data (SAV)...")
    raw = fetch_raw()
    df = raw.rename(columns={"SampleIDNumb": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).copy()
    df["id"] = df["id"].astype(int)
    if not df["id"].is_unique:
        df = df.reset_index(drop=True)
        df["id"] = df.index + 1

    cov_cols = [c for c in df.columns if c.startswith("cov_")]
    for c in ITEM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "decamp_2022_online_discussion.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
