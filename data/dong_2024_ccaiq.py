#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/25378894
# DOI: 10.6084/m9.figshare.25378894.v1
# License: CC BY 4.0
# Author: Xue Dong (2024)
# Paper: "Reliability and validity of the Chinese version of the Cross-Cultural
#         Academic Integrity Questionnaire: CCAIQ-2"
# 332 participants, 28 items from first pre-test SPSS file
# Items: cheating (6), collusion (4), complying (3), BE (3), EE (5+EE5_A), CE (6)
# Response scale: 1-6

import os
import io
import requests
import pyreadstat
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# First pre-test SPSS file (332 participants, 28 response items + 3 subscale aggregates)
DATA_URL = "https://ndownloader.figshare.com/files/44967961"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Download the SPSS file
    resp = requests.get(DATA_URL, headers=HEADERS, allow_redirects=True)
    resp.raise_for_status()

    df, meta = pyreadstat.read_sav(io.BytesIO(resp.content))

    # Create id from row index (no person ID column)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    # Covariates: 序号 (sequence number, not a person ID — drop it), 年级 (grade),
    # 专业 (major), 性别 (gender)
    cov_rename = {
        "年级": "cov_grade",
        "专业": "cov_major",
        "性别": "cov_gender",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    # Drop the sequence number column (序号) and aggregate columns (作弊, 串通, 守规)
    drop_cols = ["序号", "作弊", "串通", "守规"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Two distinct instruments in this file — one file per scale per IRW standard
    scales = {
        "dong_2024_ccaiq.csv": [
            "cheating1", "cheating2", "cheating3", "cheating4", "cheating5", "cheating6",
            "collusion1", "collusion2", "collusion3", "collusion4",
            "complying1", "complying2", "complying3",
        ],
        "dong_2024_engagement.csv": [
            "BE1", "BE2", "BE3",
            "EE1", "EE2", "EE3", "EE4", "EE5", "EE5_A",
            "CE1", "CE2", "CE3", "CE4", "CE5", "CE6",
        ],
    }

    for out_name, item_cols in scales.items():
        long = df.melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 6)].reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]

        out_path = os.path.join(OUT_DIR, out_name)
        long.to_csv(out_path, index=False)
        print(
            f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
            f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
        )


if __name__ == "__main__":
    convert()
