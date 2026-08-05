#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0215433
# DOI: 10.1371/journal.pone.0215433
#
# Ahmed A, Dompreh E, Gasparatos A (2019) Human wellbeing outcomes of
# involvement in industrial crop production: Evidence from sugarcane, oil
# palm and jatropha sites in Ghana. PLoS ONE.
#
# S3 File (XLSX, N=850 farming households in Ghana), sheet "Food
# Consumption Score": raw Food Consumption Score (FCS) items -- number of
# days (0-7) each of 14 food groups (cereals, roots/tubers, vegetables,
# fruit, meat/fish, milk, oil, sugar, etc., labelled G1-G14 in the raw
# file) was consumed in the past 7 days. Excluded "Meals", "Staple",
# "Pulses", ..., "Total" columns -- those are group-aggregated FCS
# subtotals/weighted composite, not raw per-item responses. See
# ahmed_2019_wellbeing for the companion subjective wellbeing scale from
# the same survey/sample.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0215433.s003"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"G{i}" for i in range(1, 15)]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="Food Consumption Score")


def convert():
    print("Fetching S3 File (XLSX), sheet 'Food Consumption Score'...")
    raw = fetch_raw()

    d = raw[["ID"] + ITEM_COLS].copy()
    d = d.rename(columns={"ID": "id"})
    for c in ITEM_COLS:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # Valid range for FCS food-group frequency items is 0-7 days/week.
    long = long[(long["resp"] >= 0) & (long["resp"] <= 7)].reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "ahmed_2019_food_consumption.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
