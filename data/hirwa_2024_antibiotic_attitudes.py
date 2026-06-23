#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/Attitude_related_answers_/24448688
# DOI supplement: 10.1371/journal.pone.0300742.s006
# Paper DOI: 10.1371/journal.pone.0300742
# License: CC BY 4.0
# Authors: Hirwa et al. (2024) — first author Elise M. Hirwa
# 441 participants, 9 items (attitudes toward antibiotic use/resistance, scored 0-2)

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Download URL via DOI redirect
DATA_URL = "https://doi.org/10.1371/journal.pone.0300742.s006"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Download the Excel file
    resp = requests.get(DATA_URL, headers=HEADERS, allow_redirects=True)
    resp.raise_for_status()

    # Read raw: has 3 banner rows before the real header
    raw = pd.read_excel(io.BytesIO(resp.content), sheet_name="Sheet1", header=None)
    # Row 3 (index 3) = column headers; data starts at row 4 (index 4)
    headers = list(raw.iloc[3])
    data = raw.iloc[4:].copy()
    data.columns = headers
    data = data.reset_index(drop=True)

    # Rename SN -> id
    data = data.rename(columns={"SN": "id"})
    data["id"] = pd.to_numeric(data["id"], errors="coerce")
    data = data.dropna(subset=["id"]).copy()
    data["id"] = data["id"].astype(int)

    # All other columns are item text (9 items) — no demographic covariates in this file
    item_cols = [c for c in data.columns if c != "id"]

    # Assign generic labels item_01..item_09 since column names are full question text
    item_mapping = {col: f"item_{i+1:02d}" for i, col in enumerate(item_cols)}
    data = data.rename(columns=item_mapping)
    item_cols_renamed = list(item_mapping.values())

    # Melt to long format
    long = data.melt(
        id_vars=["id"],
        value_vars=item_cols_renamed,
        var_name="item",
        value_name="resp",
    )

    # Clean responses — valid range 0-2
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 2)].reset_index(drop=True)

    # Enforce column order
    long = long[["id", "item", "resp"]]

    out_name = "hirwa_2024_antibiotic_attitudes.csv"
    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)

    print(
        f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
    )

    # Print item text mapping for reference
    print("\nItem text mapping:")
    for orig, label in item_mapping.items():
        print(f"  {label}: {orig}")


if __name__ == "__main__":
    convert()
