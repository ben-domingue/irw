#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268509
# DOI: 10.1371/journal.pone.0268509
#
# Karpudewan M, Krishnan P, Ali MN, Fah LY (2022) Designing instrument to
# measure STEM teaching practices of Malaysian teachers. PLoS ONE.
#
# S2 Dataset (XLSX, "EFA dataset", N=300 Malaysian STEM teachers): the
# exploratory-factor-analysis sample for the initial 33-item version of
# the STEM Teaching Practices questionnaire (5-point Likert per the paper
# text; observed raw range is 1-4). Four constructs: STP (STEM Teaching
# Practices, 10 items), KN (teacher knowledge, 9 items), CH (challenges
# limiting STEM teaching, 10 items), PSE (self-efficacy, 4 items).
# Companion CCA-validation sample (different respondents, reduced/renamed
# 29-item version) shipped separately as karpudewan_2022_stp_cca.
#
# One isolated data-entry error found and dropped: KN1 == 33 for a single
# respondent (scale is 1-4; a single out-of-range 33 against ~300
# otherwise-valid KN1 responses is not a real scale point).

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0268509.s005"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = (
    [f"STP{i}" for i in range(1, 11)]
    + [f"KN{i}" for i in range(1, 10)]
    + [f"CH{i}" for i in range(1, 11)]
    + [f"PSE{i}" for i in range(1, 5)]
)


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="EFA dataset")


def convert():
    print("Fetching S2 Dataset (XLSX), sheet 'EFA dataset'...")
    raw = fetch_raw()

    d = raw[["ID"] + ITEM_COLS].copy()
    d = d.rename(columns={"ID": "id"})
    for c in ITEM_COLS:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # Declared Likert range is 1-5 (observed 1-4); drop the single KN1=33
    # data-entry error and any other out-of-range values.
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "karpudewan_2022_stp_efa.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
