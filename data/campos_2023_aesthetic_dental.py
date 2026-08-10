#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0287235
# DOI: 10.1371/journal.pone.0287235
#
# Campos et al. (2023) "Aesthetic dental treatment, orofacial appearance,
# and life satisfaction of Finnish and Brazilian adults." PLOS ONE.
# License: CC BY 4.0.
#
# S1 File (XLSX, sheet "DB", N=7593: Finnish + Brazilian adults) has raw
# item-level responses for three scales, one file per scale
# (datastandard.md "one scale per file"):
#   - Orofacial Esthetic Scale (OES): OES01-07 (7 items, 0-10 scale)
#   - Psychosocial Impact of Dental Aesthetics Questionnaire (PIDAQ):
#     PIDAQ01-24 (24 items, 0-4 scale)
#   - Satisfaction with Life Scale (SWLS): SWLS01-05 (5 items, 1-7 scale)

import os

import pandas as pd
import requests
import io

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0287235.s004"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "country": "cov_country",
    "age": "cov_age",
    "sex": "cov_sex",
    "marital_status": "cov_marital_status",
    "month_income": "cov_income",
}

SCALES = {
    "campos_2023_oes": ([f"OES{i:02d}" for i in range(1, 8)], 0, 10),
    "campos_2023_pidaq": ([f"PIDAQ{i:02d}" for i in range(1, 25)], 0, 4),
    "campos_2023_swls": ([f"SWLS{i:02d}" for i in range(1, 6)], 1, 7),
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="DB")


def convert():
    print("Fetching S1 File (XLSX, sheet DB)...")
    raw = fetch_raw()
    df = raw.rename(columns=COV_RENAME)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].is_unique, "id column not unique"

    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, (item_cols, lo, hi) in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        for c in item_cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
