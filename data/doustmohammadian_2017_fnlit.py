#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0179196
# DOI: 10.1371/journal.pone.0179196
#
# Doustmohammadian A, Omidvar N, Keshavarz-Mohammadi N, Abdollahi M, Amini M,
# Eini-Zinab H (2017) Developing and validating a scale to measure Food and
# Nutrition Literacy (FNLIT) in elementary school children in Iran.
# PLoS ONE 12(6): e0179196.
#
# S3 File (SAV) contains item-level responses to the FNLIT scale (N=373
# elementary school children), scored 0-4 across many sub-domains
# (Foodknowledge_*, Lifestyle_*, Foodsafty_*, Understanding_*, Foodscience_*,
# Avaiability_*, Foodchoice_*, Eatingbehav_*, Interactive_*, Critical_*).
# All sub-domains belong to the single FNLIT instrument, so they are shipped
# as one file. The "Code" column has 2 coincidental duplicate values among
# 373 distinct children (confirmed via differing sex/age/school), so the
# row index is used as `id` instead.

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0179196.s007"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

NON_ITEM_COLS = {"Code", "Doc_area", "sex", "Class", "School_Code", "Age_y"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp_path = "/tmp/_doustmohammadian_2017_s3.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp_path, apply_value_formats=False)
    os.remove(tmp_path)
    return df


def convert():
    print("Fetching S3 File (SAV)...")
    raw = fetch_raw()
    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)  # Code has coincidental duplicates; use row index

    item_cols = [c for c in raw.columns if c not in NON_ITEM_COLS and c != "id"]

    long = raw.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "doustmohammadian_2017_fnlit.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
