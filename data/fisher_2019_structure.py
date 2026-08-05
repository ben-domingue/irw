#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0209279
# DOI: 10.1371/journal.pone.0209279
#
# Fisher AJ, Mendoza-Denton R, Patt C, et al. (2019) Structure and
# belonging: Pathways to success for underrepresented minority and women
# PhD students in STEM fields. PLoS ONE.
#
# S1 Data (XLSX, N=499 STEM PhD students). Per the paper's Measures
# section, perceived "departmental structure" was measured with 2 raw
# items: "the academic expectations of the department for graduate
# students are appropriate" (expectations) and "the performance standards
# graduate students are held to are appropriate" (standards). Shipped as
# its own 2-item table. Companion scales from the same survey/sample:
# fisher_2019_belonging (2 items) and fisher_2019_preparedness (2 items).

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0209279.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["expectations", "standards"]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="newdat")


def convert():
    print("Fetching S1 Data (XLSX)...")
    raw = fetch_raw()

    d = raw[["id"] + ITEM_COLS].copy()
    for c in ITEM_COLS:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "fisher_2019_structure.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
