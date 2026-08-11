#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0191632
# DOI: 10.1371/journal.pone.0191632
#
# Yang, Operario, Zaller et al. (2018) "Depression and its correlations
# with health-risk behaviors and social capital among female migrants
# working in entertainment venues in China." PLOS ONE. CC BY 4.0.
#
# S1 Dataset (SAV, N=358) contains raw CES-D-style depression items
# (E1-E20; see yang_2018_cesd.py) and a parallel 20-item anxiety scale
# (E21-E40, 1-4 scale) -- this script produces the anxiety table. All
# other columns in the file are demographic/risk-behavior covariates or
# precomputed subscale sums (depressionS, anxietyS, TotalC2, D6total,
# SocialCapital, etc.) and are excluded per the composite-exclusion rule.

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0191632.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"E{i}" for i in range(21, 41)]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_yang_2018_0191632_s1.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, meta = pyreadstat.read_sav(tmp)
    os.remove(tmp)
    return df


def convert():
    print("Fetching S1 Dataset (SAV)...")
    df = fetch_raw()

    df = df.rename(columns={"ID1": "id"})
    assert df["id"].nunique() == len(df), "id column not unique"
    df["id"] = df["id"].astype(int)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 4)].reset_index(drop=True)

    long = long[["id", "item", "resp"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "yang_2018_anxiety.csv")
    long.to_csv(out_path, index=False)

    print(f"yang_2018_anxiety: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
