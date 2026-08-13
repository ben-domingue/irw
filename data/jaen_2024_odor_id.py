#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0301264
# DOI: 10.1371/journal.pone.0301264
#
# "Remote olfactory assessment using the NIH Toolbox Odor Identification test
# and the brain health registry" -- participants (recruited via the Brain
# Health Registry) each identified 9 odors (from the Monell/NIH Toolbox Odor
# Identification test) as a 4-alternative multiple choice task; the "NIH
# Tolbox Sensory items" sheet in S1 Data already records per-item Yes/No
# (correct/incorrect identification) for each of the 9 odors. CC BY 4.0.

import io
import os

import openpyxl
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0301264.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["lemon", "playdoh", "bubblegum", "chocolate", "popcorn",
             "coffee", "smoke", "naturalgas", "flower"]


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    wb = openpyxl.load_workbook(io.BytesIO(r.content))
    ws = wb["NIH Tolbox Sensory items"]
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    header = rows[0]
    df = pd.DataFrame(rows[1:], columns=header)

    df = df.rename(columns={
        "login": "id",
        "ethncty": "cov_ethnicity",
        "age": "cov_age",
        "gender": "cov_gender",
        "Race": "cov_race",
    })
    df = df.drop(columns=["assmnt"])  # all rows are "Baseline"

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per row"

    cov_cols = ["cov_ethnicity", "cov_age", "cov_gender", "cov_race"]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")

    resp_map = {"Yes": 1, "No": 0}
    long["resp"] = long["resp"].map(resp_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "jaen_2024_odor_id.csv")
    long.to_csv(out_path, index=False)
    print(f"jaen_2024_odor_id: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
