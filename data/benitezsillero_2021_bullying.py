#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259087
# DOI: 10.1371/journal.pone.0259087
# SI: S1 File (10.1371/journal.pone.0259087.s001), XLSX
#
# European Bullying Intervention Project Questionnaire (EBIPQ), 14 items
# (7 victimization + 7 aggression), 0-4 frequency scale. "mvicbull" and
# "agrebull" are the mean victimization/aggression composite scores -
# excluded. No person id column in the source file; row index used.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0259087.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Hoja1")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns={"edad": "cov_age", "Sex": "cov_sex"})
    df["cov_sex"] = df["cov_sex"].map({"Chico": "male", "Chica": "female"}).fillna(df["cov_sex"])

    item_cols = [f"EBIPQ_{i}" for i in range(1, 15)]
    cov_cols = ["cov_age", "cov_sex"]

    long = df[["id"] + cov_cols + item_cols].melt(
        id_vars=["id"] + cov_cols, value_vars=item_cols,
        var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 4)]
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "benitezsillero_2021_bullying.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
