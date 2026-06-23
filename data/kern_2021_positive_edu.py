#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/14870235
# DOI: 10.6084/m9.figshare.14870235.v1
# Figshare download: https://ndownloader.figshare.com/files/28626591
# License: CC0 (public domain)
#
# Dataset: Positive Education Tertiary
# 350 respondents, 37 items across 5 scales:
#   C1-C9   : Connectedness scale (9 items, Likert 1-4)
#   E1-E9   : Engagement scale (9 items, Likert 1-4)
#   L1-L12  : Learning scale (12 items, Likert 1-4)
#   SHS1-3  : Subjective Happiness Scale (3 items, Likert 1-7)
#   SWLS1-4 : Satisfaction with Life Scale (4 items, Likert 1-7)
#
# Each scale is saved as a separate CSV per IRW standard.
# No explicit participant ID column — constructed from row index.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

DOWNLOAD_URL = "https://ndownloader.figshare.com/files/28626591"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "kern_2021_connectedness.csv": {
        "items": [f"C{i}" for i in range(1, 10)],
        "valid_min": 1, "valid_max": 4
    },
    "kern_2021_engagement.csv": {
        "items": [f"E{i}" for i in range(1, 10)],
        "valid_min": 1, "valid_max": 4
    },
    "kern_2021_learning.csv": {
        "items": [f"L{i}" for i in range(1, 13)],
        "valid_min": 1, "valid_max": 4
    },
    "kern_2021_happiness.csv": {
        "items": [f"SHS{i}" for i in range(1, 4)],
        "valid_min": 1, "valid_max": 7
    },
    "kern_2021_life_satisfaction.csv": {
        "items": [f"SWLS{i}" for i in range(1, 5)],
        "valid_min": 1, "valid_max": 7
    },
}


def download_data():
    r = requests.get(DOWNLOAD_URL, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name=0)


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = download_data()

    # Create integer id from row index (source uses "Respondent N" strings)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    # Drop the original respondent label column
    label_col = "Unnamed: 0"
    if label_col in df.columns:
        df = df.drop(columns=[label_col])

    # No person-level covariates in this dataset
    cov_cols = []

    for out_name, spec in SCALES.items():
        item_cols = spec["items"]
        valid_min = spec["valid_min"]
        valid_max = spec["valid_max"]

        long = df[["id"] + item_cols].melt(
            id_vars=["id"],
            value_vars=item_cols,
            var_name="item",
            value_name="resp"
        )

        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[long["resp"].between(valid_min, valid_max)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        # Enforce column order (no covariates in this dataset)
        long = long[["id", "item", "resp"]]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        out_path = os.path.join(OUT_DIR, out_name)
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
