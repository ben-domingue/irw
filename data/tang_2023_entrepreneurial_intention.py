#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/24081459
# DOI: 10.6084/m9.figshare.24081459.v1
# License: CC BY 4.0
# Author: Shenlong Tang (2023) - "Igniting Entrepreneurial Intention: Uncovering the
#         Influences of Transformational Leadership, Education and Training,
#         Entrepreneurial Attitude, and Moderators of Perceived Creativity"
# 271 participants, 5 scales, 5-point Likert (1-5)
# Scales:
#   TL  = Transformational Leadership (5 items: TL1-TL5)
#   ET  = Education and Training (6 items: ET1-ET6)
#   AT  = Entrepreneurial Attitude (5 items: AT1-AT5)
#   EI  = Entrepreneurial Intention (6 items: EI1-EI6)
#   PC  = Perceived Creativity (6 items: PC1-PC6)
# Each scale is output as a separate CSV per IRW standard.

import os
import io
import requests
import pandas as pd

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

ARTICLE_ID = 24081459
FIGSHARE_API = f"https://api.figshare.com/v2/articles/{ARTICLE_ID}/files"

# Scale definitions: output_name -> list of item columns
SCALES = {
    "tang_2023_transformational_leadership": ["TL1", "TL2", "TL3", "TL4", "TL5"],
    "tang_2023_entrepreneurial_training":    ["ET1", "ET2", "ET3", "ET4", "ET5", "ET6"],
    "tang_2023_entrepreneurial_attitude":    ["AT1", "AT2", "AT3", "AT4", "AT5"],
    "tang_2023_entrepreneurial_intention":   ["EI1", "EI2", "EI3", "EI4", "EI5", "EI6"],
    "tang_2023_perceived_creativity":        ["PC1", "PC2", "PC3", "PC4", "PC5", "PC6"],
}


def convert():
    # 1. Get download URL from figshare API
    resp = requests.get(FIGSHARE_API, headers=HEADERS)
    resp.raise_for_status()
    files = resp.json()
    # Single file: Data.csv
    target = next(f for f in files if f["name"].endswith(".csv"))

    raw = requests.get(target["download_url"], headers=HEADERS)
    raw.raise_for_status()

    df = pd.read_csv(io.StringIO(raw.text))

    # 2. Rename ID column
    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).copy()
    df["id"] = df["id"].astype(int)

    # 3. Covariates
    cov_rename = {
        "Gender": "cov_gender",
        "Age": "cov_age",
        "Grade": "cov_grade",
        "Major": "cov_major",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    os.makedirs(OUT_DIR, exist_ok=True)

    # 4. Loop over scales and produce one file each
    for out_name, item_cols in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()

        long = sub.melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp"
        )

        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # Valid range 1-5
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

        # Enforce column order
        long = long[["id", "item", "resp"] + cov_cols]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)

        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
