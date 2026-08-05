#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0215433
# DOI: 10.1371/journal.pone.0215433
#
# Ahmed A, Dompreh E, Gasparatos A (2019) Human wellbeing outcomes of
# involvement in industrial crop production: Evidence from sugarcane, oil
# palm and jatropha sites in Ghana. PLoS ONE.
#
# S3 File (XLSX, N=850 farming households in Ghana) has 4 sheets: MPI
# (Multidimensional Poverty Index -- pre-weighted/derived deprivation
# indicators, not raw items), Demographics Used (household covariates),
# Food Consumption Score (raw 7-day food-group consumption frequencies --
# shipped separately as ahmed_2019_food_consumption), and Subjective
# Wellbeing (this file) -- 4 raw ONS4-style wellbeing items (life
# satisfaction, worthwhile, happiness, anxiety) on a 1-4 scale.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0215433.s003"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["Statisfaction", "Worthwhile", "Happiness", "Anxious"]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="Subjective Wellbeing")


def convert():
    print("Fetching S3 File (XLSX), sheet 'Subjective Wellbeing'...")
    raw = fetch_raw()

    d = raw[["ID"] + ITEM_COLS].copy()
    d = d.rename(columns={"ID": "id"})
    for c in ITEM_COLS:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "ahmed_2019_wellbeing.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
