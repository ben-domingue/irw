#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0262418
# DOI: 10.1371/journal.pone.0262418
#
# Dahlstrom EK, Bell C, Chang S, Lee HY, Anderson CB, Pham A, et al. (2022)
# Translating mentoring interventions research into practice: Evaluation
# of an evidence-based workshop for research mentors on developing
# trainees' scientific communication skills. PLoS ONE.
#
# S1 Dataset (XLSX, N=160 SCOARE workshop participants across 2 program
# years). Post-workshop survey used a retrospective pre-post design:
# participants rated skill/knowledge items both "Before" the workshop and
# "Now" (immediately after), 0-3 scale. Source column names encode
# <construct><B|N> (e.g. SFB = construct "SF" Before, SFN = construct
# "SF" Now); Year-2 added a Work/Science-context split for some
# constructs (e.g. SFWB/SFWN/SFSB/SFSN). Melted to long format with the
# B/N suffix mapped to a `wave` column (0=Before, 1=Now) and the
# remaining stem used as `item`. Different constructs were asked in
# different program years, so per-item N varies (65-158); this is
# expected, not an error -- rows are simply absent where a construct
# wasn't asked that year.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0262418.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    xls = pd.ExcelFile(pd.io.common.BytesIO(r.content))
    return pd.read_excel(xls, sheet_name=xls.sheet_names[0])


def convert():
    print("Fetching S1 Dataset (XLSX)...")
    raw = fetch_raw()

    item_cols = [c for c in raw.columns if c != "ID"]
    d = raw[["ID"] + item_cols].copy()
    d = d.rename(columns={"ID": "id"})
    for c in item_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="raw_item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 3)].reset_index(drop=True)

    suffix = long["raw_item"].str[-1]
    long["item"] = long["raw_item"].str[:-1]
    long["wave"] = suffix.map({"B": 0, "N": 1}).astype(int)
    long = long[["id", "item", "resp", "wave"]].sort_values(["id", "item", "wave"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "dahlstrom_2022_scoare.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
