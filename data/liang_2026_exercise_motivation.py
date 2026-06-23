#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/Exercise_motivation_questionnaire_dataset_/26047004
# DOI: 10.1371/journal.pone.0345759.s002  (supplementary data file)
# License: CC BY 4.0
# Authors: Xilin Liang, Zenan Wang (2026)
# Dataset: Exercise motivation questionnaire (45 participants)
# Two scales: Intrinsic Motivation (IM1-IM5) and Extrinsic Motivation (EM1-EM5)

import os
import io
import requests
import pandas as pd

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

DATA_URL = "https://doi.org/10.1371/journal.pone.0345759.s002"


def download_csv():
    r = requests.get(DATA_URL, headers=HEADERS, allow_redirects=True)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = download_csv()

    # id column
    df = df.rename(columns={"participant_id": "id"})

    # Covariates
    cov_rename = {
        "gender": "cov_gender",
        "age": "cov_age",
        "professionalbackground": "cov_professional_background",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    # Use numeric (_num) columns for responses; drop the text versions
    text_items = [c for c in df.columns if c in
                  ["IM1", "IM2", "IM3", "IM4", "IM5",
                   "EM1", "EM2", "EM3", "EM4", "EM5"]]
    df = df.drop(columns=text_items)

    # Intrinsic motivation: IM1_num - IM5_num
    im_cols = [c for c in df.columns if c.startswith("IM") and c.endswith("_num")]
    # Extrinsic motivation: EM1_num - EM5_num
    em_cols = [c for c in df.columns if c.startswith("EM") and c.endswith("_num")]

    # Rename _num columns to clean item names (IM1, IM2, ... EM1, EM2, ...)
    rename_map = {c: c.replace("_num", "") for c in im_cols + em_cols}
    df = df.rename(columns=rename_map)
    im_cols_clean = [c.replace("_num", "") for c in im_cols]
    em_cols_clean = [c.replace("_num", "") for c in em_cols]

    scales = [
        ("liang_2026_intrinsic_motivation", im_cols_clean),
        ("liang_2026_extrinsic_motivation", em_cols_clean),
    ]

    for out_name, item_cols in scales:
        long = df[["id"] + cov_cols + item_cols].melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        # Enforce column order
        long = long[["id", "item", "resp"] + cov_cols]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(
            f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
            f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
        )


if __name__ == "__main__":
    convert()
