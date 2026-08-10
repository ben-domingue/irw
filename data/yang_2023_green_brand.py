#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0292633
# DOI: 10.1371/journal.pone.0292633
#
# Yang et al. (2023) "The influence of the brand image of green agriculture
# products on China's consumption intention: The mediating role of
# perceived value." PLOS ONE. License: CC BY 4.0.
#
# S1 File (CSV, N=341) has raw survey responses, 5-point Likert (1=disagree,
# 5=agree). Three constructs, split into separate scale files per
# datastandard.md ("one scale per file"):
#   - Green agricultural brand image: A1-A3, B1-B3, C1,C2,C4, D1-D3 (12 items,
#     matches paper's "4 dimensions with 12 indicators total"; note C3 is
#     absent from the raw file -- dropped item, not our omission)
#   - Customer perceived value: E1-E3 (3 items)
#   - Consumption intention: F1-F4 (4 items)

import os
import io

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0292633.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Education background": "cov_education",
    "Monthly income": "cov_income",
}

SCALES = {
    "yang_2023_green_brand_image": ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C4", "D1", "D2", "D3"],
    "yang_2023_perceived_value": ["E1", "E2", "E3"],
    "yang_2023_consumption_intent": ["F1", "F2", "F3", "F4"],
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def convert():
    print("Fetching S1 File (CSV)...")
    raw = fetch_raw()
    df = raw.rename(columns=COV_RENAME)
    # "NO." has one duplicate value (row 235) -- use row index as id instead,
    # per datastandard.md guidance for non-unique source ids.
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].is_unique, "id column not unique"

    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, item_cols in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        for c in item_cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
