#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0286923
# DOI: 10.1371/journal.pone.0286923
#
# "Perceived value and its relationship to satisfaction and loyalty in
# cultural coastal destinations: A study in Huanchaco, Peru". Despite the
# Data Availability statement's ambiguous "will be made available" wording,
# S1 File (.s001, SPSS .sav) is already the raw per-respondent item data
# (N=384) -- verified identical to S2 File (.s002), so only S1 is used here.
# Item columns are 19 five-point Likert items covering satisfaction (P2_1),
# loyalty intentions (P3_1-3), and perceived value (P4_1-15); P5-P12 are
# demographic covariates (nationality, gender, marital status, age,
# education, occupation, travel companion, income). No PII. CC BY 4.0.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0286923.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "P5": "cov_nationality",
    "P6": "cov_gender",
    "P7": "cov_marital_status",
    "P8": "cov_age",
    "P9": "cov_education",
    "P10": "cov_occupation",
    "P11": "cov_travel_companion",
    "P12": "cov_income",
}

ITEM_COLS = (
    ["P2_1"] + [f"P3_{i}" for i in range(1, 4)] + [f"P4_{i}" for i in range(1, 16)]
)


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = os.path.join(OUT_DIR, "_tmp_regalado_2023.sav")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(tmp, "wb") as f:
        f.write(r.content)

    import pyreadstat
    df, meta = pyreadstat.read_sav(tmp)
    os.remove(tmp)

    df = df.rename(columns={"ID": "id"})
    df = df.rename(columns=COV_COLS)
    cov_cols = list(COV_COLS.values())

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per row"

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_path = os.path.join(OUT_DIR, "regalado_2023_tourism_value.csv")
    long.to_csv(out_path, index=False)
    print(f"regalado_2023_tourism_value: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
