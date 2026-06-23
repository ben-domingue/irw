#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/24081459
# DOI: 10.6084/m9.figshare.24081459.v1
# License: CC BY 4.0
# Author: Shenlong Tang (2024)
# Paper: "Igniting Entrepreneurial Intention: Uncovering the Influences of
#         Transformational Leadership, Education and Training, Entrepreneurial
#         Attitude, and Moderators of Perceived Creativity"
# 271 participants, 28 items across 5 scales, 1-5 Likert
# Scales: TL (Transformational Leadership, 5), ET (Education & Training, 6),
#         AT (Entrepreneurial Attitude, 5), EI (Entrepreneurial Intention, 6),
#         PC (Perceived Creativity, 6)

import os
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DATA_URL = "https://ndownloader.figshare.com/files/42254256"

# All five scales — produce one combined file (single instrument study)
ITEM_COLS = [
    "TL1", "TL2", "TL3", "TL4", "TL5",
    "ET1", "ET2", "ET3", "ET4", "ET5", "ET6",
    "AT1", "AT2", "AT3", "AT4", "AT5",
    "EI1", "EI2", "EI3", "EI4", "EI5", "EI6",
    "PC1", "PC2", "PC3", "PC4", "PC5", "PC6",
]


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    resp = requests.get(DATA_URL, headers=HEADERS, allow_redirects=True)
    resp.raise_for_status()

    import io
    df = pd.read_csv(io.BytesIO(resp.content))

    # Rename ID -> id
    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).copy()
    df["id"] = df["id"].astype(int)

    # Covariates
    cov_rename = {
        "Gender": "cov_gender",
        "Age": "cov_age",
        "Grade": "cov_grade",
        "Major": "cov_major",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    # Melt to long format
    long = df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )

    # Clean responses — valid range 1-5
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)

    # Enforce column order
    long = long[["id", "item", "resp"] + cov_cols]

    out_name = "tang_2024_entrepreneurial_intention.csv"
    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)

    print(
        f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
    )


if __name__ == "__main__":
    convert()
