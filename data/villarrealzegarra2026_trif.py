from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Telemedicine Readiness Inventory for Facilities (TRI-F): "
         "Adaptation and Psychometric Validation across a National Health "
         "System (Villarreal-Zegarra, 2026, figshare)")
URL  = "https://figshare.com/articles/dataset/Adaptation_and_Psychometric_Validation_of_the_Inventory_to_Assess_the_Telemedicine_Readiness_of_Primary_Care_Facilities/32514540"
DOI  = "10.64898/2026.07.01.26356790"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/65528874"

# p1:p85 is treated as one unified item pool in the source analysis script
# (dimension-level factor models are fit on subsets of it, but the R plan
# doesn't map specific p-numbers to named dimensions) -- kept as a single
# instrument file rather than guessing a split.
COV_COLS = {
    "sexo": "cov_sex",
    "edad_cat": "cov_age_cat",
    "profesion": "cov_profession",
    "especialidad": "cov_specialty",
    "categoria": "cov_facility_category",
    "macro_region": "cov_macro_region",
    "region": "cov_region",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_stata(pd.io.common.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def convert():
    print("Downloading Database.dta ...")
    raw = fetch_data()
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)
    cov_cols = list(cov.columns.drop("id"))

    item_cols = [f"p{i}" for i in range(1, 86)]
    items = raw[["id"] + item_cols].merge(cov, on="id")
    long = items.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "villarrealzegarra2026_trif.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
