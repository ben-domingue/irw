#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/6SVFUJ
# DOI: 10.7910/dvn/6svfuj
# License: CC0
# Dataset: OSCE clinical examination — interns' contact precautions checklist
# 269 participants, 15 binary checklist items, 2 waves (sessions)

import os
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Dataverse file ID for the .tab file (Dataset 1: interns' checklist scores)
FILE_ID = 3610467
URL = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Download
    resp = requests.get(URL, headers=HEADERS)
    resp.raise_for_status()

    from io import StringIO
    df = pd.read_csv(StringIO(resp.text), sep="\t")

    # Columns:
    # AY: academic year cohort (1516, 1617)
    # ID: participant identifier
    # Session1, Session2: session date strings
    # PriorTraining: covariate
    # ContPrec1-15: session 1 responses (strings: '0', '1', '#NULL!')
    # ContPrec1b-15b: session 2 responses (numeric: 0.0, 1.0, NaN)

    item_cols_s1 = [f"ContPrec{i}" for i in range(1, 16)]
    item_cols_s2 = [f"ContPrec{i}b" for i in range(1, 16)]

    cov_cols = ["cov_ay", "cov_prior_training"]
    df = df.rename(columns={"AY": "cov_ay", "PriorTraining": "cov_prior_training"})

    # Session 1: 144 records (AY=1617 cohort who had both sessions)
    s1 = df[["ID", "cov_ay", "cov_prior_training"] + item_cols_s1].copy()
    # Convert '#NULL!' to NaN, then to numeric
    for col in item_cols_s1:
        s1[col] = pd.to_numeric(s1[col].replace("#NULL!", None), errors="coerce")
    # Keep only rows that have at least one valid response in session 1
    s1 = s1.dropna(subset=item_cols_s1, how="all")

    long_s1 = s1.melt(
        id_vars=["ID", "cov_ay", "cov_prior_training"],
        value_vars=item_cols_s1,
        var_name="item",
        value_name="resp"
    )
    long_s1["wave"] = 1
    # Rename item cols: ContPrec1 -> ContPrec_1
    long_s1["item"] = long_s1["item"].str.replace(r"ContPrec(\d+)", r"ContPrec_\1", regex=True)

    # Session 2: all 269 records
    s2 = df[["ID", "cov_ay", "cov_prior_training"] + item_cols_s2].copy()
    for col in item_cols_s2:
        s2[col] = pd.to_numeric(s2[col], errors="coerce")

    long_s2 = s2.melt(
        id_vars=["ID", "cov_ay", "cov_prior_training"],
        value_vars=item_cols_s2,
        var_name="item",
        value_name="resp"
    )
    long_s2["wave"] = 2
    # Rename item cols: ContPrec1b -> ContPrec_1
    long_s2["item"] = long_s2["item"].str.replace(r"ContPrec(\d+)b", r"ContPrec_\1", regex=True)

    # Combine
    long = pd.concat([long_s1, long_s2], ignore_index=True)
    long = long.rename(columns={"ID": "id"})

    # Clean responses
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # Filter to valid binary values (0 or 1)
    long = long[long["resp"].isin([0.0, 1.0])].reset_index(drop=True)

    # Enforce column order
    long = long[["id", "item", "resp", "wave", "cov_ay", "cov_prior_training"]]

    out_name = "nakano_2020_osce_contact_precautions.csv"
    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)

    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
