#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/16900393
# DOI: 10.6084/m9.figshare.16900393.v2
# Authors: Marcos Rosetti, Alexa Sarai Ramírez
# License: CC BY 4.0
# 468 participants, scales: GAD7 (7 items, 0-3), CAS (22 items, 0-4)
# CCKQ (correct/incorrect strings) and EconGame (choice-based) are excluded
# as they are not Likert-type psychometric items.

import os
import io
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

DOWNLOAD_URL = "https://ndownloader.figshare.com/files/40839032"

SCALES = {
    "rosetti_2023_gad7": {
        "items": [f"GAD7_q{i}" for i in range(1, 8)],
        "valid_range": (0, 3),
    },
    "rosetti_2023_cas": {
        "items": [f"CAS_q{i}" for i in range(1, 23)],
        "valid_range": (0, 4),
    },
}


def convert():
    headers = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
    r = requests.get(DOWNLOAD_URL, headers=headers, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))

    # id column is already named 'id' but is a string like 'R1', 'R10', ...
    # Use row index as numeric id instead (as per data standard for non-numeric string IDs)
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    # Covariates
    cov_rename = {
        "age": "cov_age",
        "gender": "cov_gender",
        "t.soc.net": "cov_social_net_time",
        "t.news": "cov_news_time",
        "scale": "cov_scale_group",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)

    for out_name, spec in SCALES.items():
        item_cols = spec["items"]
        valid_min, valid_max = spec["valid_range"]

        long = df[["id"] + cov_cols + item_cols].melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )

        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= valid_min) & (long["resp"] <= valid_max)]

        # Enforce column order
        resp_level = [c for c in long.columns if c in ("wave", "treat", "rt", "date")]
        long = long[["id", "item", "resp"] + resp_level + cov_cols]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(
            f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
            f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
        )


if __name__ == "__main__":
    convert()
