#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0321066
# DOI: 10.1371/journal.pone.0321066
#
# Jiang N, Li H, Ju SY, Kong LK, Li J (2025) Pre-service teachers'
# empathy and attitudes toward inclusive education -- The chain
# mediating role of teaching motivation and inclusive education
# efficacy. PLoS ONE.
#
# S1 Data (XLSX, N=240 Chinese pre-service teachers). Revised Motivation
# for Teacher Education Questionnaire (Schepens et al. 2009), 4 items
# across 2 dimensions: professional love (PL1-2) and educational interest
# (EI1-2), 6-point Likert (1-6). Companion scales from the same
# survey/sample: jiang_2025_sacie (15 items), jiang_2025_inclusive_efficacy
# (18 items), jiang_2025_empathy (7 items).

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0321066.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["PL1", "PL2", "EI1", "EI2"]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    xls = pd.ExcelFile(pd.io.common.BytesIO(r.content))
    return pd.read_excel(xls, sheet_name=xls.sheet_names[0])


def convert():
    print("Fetching S1 Data (XLSX)...")
    raw = fetch_raw()

    d = raw[["ID"] + ITEM_COLS].copy()
    d = d.rename(columns={"ID": "id"})
    for c in ITEM_COLS:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 6)].reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "jiang_2025_teaching_motivation.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
