#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268509
# DOI: 10.1371/journal.pone.0268509
#
# Karpudewan M, Krishnan P, Ali MN, Fah LY (2022) Designing instrument to
# measure STEM teaching practices of Malaysian teachers. PLoS ONE.
#
# S1 Dataset (XLSX, "CCA dataset", N=397 Malaysian STEM teachers): a
# second, independently-recruited sample used for confirmatory composite
# analysis (CCA) on the EFA-reduced 29-item version of the STEM Teaching
# Practices questionnaire. Four constructs: STP (8 items), KN (7 items),
# PD (10 items), PE (4 items). Companion EFA sample (33-item initial
# version, different respondents) shipped separately as
# karpudewan_2022_stp_efa.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0268509.s004"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = (
    [f"STP{i}" for i in range(1, 9)]
    + [f"KN{i}" for i in range(1, 8)]
    + [f"PD{i}" for i in range(1, 11)]
    + [f"PE{i}" for i in range(1, 5)]
)


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="CCA dataset")


def convert():
    print("Fetching S1 Dataset (XLSX), sheet 'CCA dataset'...")
    raw = fetch_raw()

    d = raw[["ID"] + ITEM_COLS].copy()
    d = d.rename(columns={"ID": "id"})
    for c in ITEM_COLS:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "karpudewan_2022_stp_cca.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
