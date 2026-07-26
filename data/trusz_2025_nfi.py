from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

DOI   = "10.7910/DVN/DWCBOE"
TITLE = ("Datasets and materials underlying the Study on The Need "
         "Fulfillment Inventory for Older Adults Participating in "
         "University of the Third Age Activities: Development and "
         "Psychometric Properties")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_ID = 13673103  # EFA_NFI72_N660.sav

COV_MAP = {
    "PLEC":      "cov_gender",       # 1/2
    "WIEK":      "cov_age",
    "EMERYTURA": "cov_years_retired",
    "PRACA":     "cov_still_working",  # 0/1
    "STANCYWIL": "cov_marital_status",
    "EDU":       "cov_education",
    "MZAM":      "cov_residence",
}

ITEM_COLS = [f"i{i}" for i in range(1, 73)]  # raw 1-5 Likert, NFI-72


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    df, _meta = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    print("Downloading EFA_NFI72_N660.sav …")
    df = fetch_data()

    df = df.rename(columns={"lp": "id", **COV_MAP})
    assert df["id"].nunique() == len(df), "id column is not unique per row"
    df["id"] = df["id"].astype(int)

    cov_cols = list(COV_MAP.values())
    keep = ["id"] + cov_cols + ITEM_COLS
    df = df[keep].copy()

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # -1 sentinel check: valid NFI-72 scale is 1-5
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    col_order = ["id", "item", "resp"] + cov_cols
    long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "trusz_2025_nfi.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
