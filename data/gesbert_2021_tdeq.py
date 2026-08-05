#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0246823
# DOI: 10.1371/journal.pone.0246823
#
# Gesbert V, et al. (2021) Reviewing the role of the environment in the
# talent development of a professional soccer club. PLoS ONE.
#
# S1 Data (XLSX, N=64 unique Swiss elite youth players, identified by
# CODE) has the raw 25-item Talent Development Environment Questionnaire
# (TDEQ), 1-6 scale. The file also includes 7 "<item> inverse" columns
# (Q1/Q5/Q7/Q11/Q12/Q16/Q24 inversé) which are just 7-minus-raw-value
# reverse-scored duplicates of those same items (confirmed: Q1_inverse ==
# 7 - Q1 for every row) -- excluded as derived, not independent items.
# N=64 is below this pipeline's usual >=100 preference but above the
# hard N<50 floor; shipped per ben-domingue's explicit approval
# (2026-08-04) given the data is otherwise clean and genuinely raw.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0246823.s005"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = [f"Q{i}" for i in range(1, 26)]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content))


def convert():
    print("Fetching S1 Data (XLSX)...")
    raw = fetch_raw()

    d = raw[["CODE"] + ITEMS].dropna(subset=["CODE"]).copy()
    d = d.rename(columns={"CODE": "id"})
    assert d["id"].is_unique, "id column not unique"
    for c in ITEMS:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=ITEMS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "gesbert_2021_tdeq.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
