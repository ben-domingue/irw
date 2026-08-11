#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0294440
# DOI: 10.1371/journal.pone.0294440
# Supporting Information: S1 Data (SPSS .sav)
# https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0294440.s001

import os
import requests
import pyreadstat
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0294440.s001")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# 7-item "current academic adaptation" satisfaction scale (Likert 1-5)
ITEM_COLS = ["P1_a", "P1_b", "P1_c", "P1_d", "P1_e", "P1_f", "P1_g"]

COV_RENAME = {
    "sexo": "cov_sexo",
    "edad": "cov_edad",
    "ensenyament": "cov_field_of_study",
}


def convert():
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "corti_2023_raw.sav")
    if not os.path.exists(local_path):
        r = requests.get(SI_URL, headers=HEADERS, timeout=60)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)

    df, meta = pyreadstat.read_sav(local_path)

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    assert df["id"].nunique() == len(df), "id column is not unique per row"
    df["id"] = df["id"].astype(int)

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # Scale is documented as a 1-5 Likert item; guard against any stray
    # out-of-range / sentinel values.
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "corti_2023_academic_adaptation.csv")
    long.to_csv(out_path, index=False)
    print(f"corti_2023_academic_adaptation.csv: rows={len(long)} "
          f"ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    if os.path.exists(local_path):
        os.remove(local_path)


if __name__ == "__main__":
    convert()
