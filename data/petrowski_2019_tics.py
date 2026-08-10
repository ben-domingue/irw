#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0222277
# DOI: 10.1371/journal.pone.0222277
#
# Petrowski et al. (2019) "Norm values and psychometric properties of the
# short version of the Trier Inventory for Chronic Stress (TICS) in a
# representative German sample." PLOS ONE. License: CC BY 4.0.
#
# S1 Data (SAV, N=2473) has the full 57-item TICS, 5-point scale
# (0=never, 1=rarely, 2=sometimes, 3=often, 4=very often), covering nine
# chronic-stress dimensions. This is the raw item pool the paper's 9- and
# 12-item short forms are derived from.

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0222277.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_petrowski_2019.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp)
    return df


def convert():
    print("Fetching S1 Data (SAV)...")
    raw = fetch_raw()
    df = raw.rename(columns={"fbnr": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).copy()
    df["id"] = df["id"].astype(int)
    assert df["id"].is_unique, "id column not unique"

    item_cols = [c for c in df.columns if c.startswith("tics")]
    assert len(item_cols) == 57

    for c in item_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[(long["resp"] >= 0) & (long["resp"] <= 4)].reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "petrowski_2019_tics.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
