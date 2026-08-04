#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0304140
# DOI: 10.1371/journal.pone.0304140
#
# Kuczyk C, Muench K, Noehre M, et al. (2024) Development and testing of a
# questionnaire on the expectations and experiences with wearing face
# masks in inpatient and day hospitals. PLoS ONE.
#
# S1 Data (SAV, N=142) has two raw multi-item 5-point agreement batteries
# (numeric-coded 1-5: 1=definitely disagree ... 5=definitely agree per the
# SAV value labels), shipped as separate scales per the column-prefix
# split: FBA_* (42 items, some individually suffixed "_pre" in the source
# column names -- no corresponding "_post" columns exist, so this is not a
# repeated-measures design, just an artifact of the source
# variable-naming) and FBE_* (27 items).

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0304140.s006"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp_path = "/tmp/_kuczyk_2024_s1.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp_path, apply_value_formats=False)
    os.remove(tmp_path)
    return df


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df[item_cols].copy()
    d["id"] = df["ID"]
    for c in item_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    print("Fetching S1 Data (SAV)...")
    raw = fetch_raw()
    fba_items = [c for c in raw.columns if c.startswith("FBA")]
    fbe_items = [c for c in raw.columns if c.startswith("FBE")]

    write_scale(build_long(raw, fba_items), "kuczyk_2024_facemask_fba.csv")
    write_scale(build_long(raw, fbe_items), "kuczyk_2024_facemask_fbe.csv")


if __name__ == "__main__":
    convert()
