from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

DOI   = "10.1371/journal.pone.0137176.s001"
TITLE = ("Rumination and Loneliness Independently Predict Six-Month "
         "Later Depression Symptoms among Chinese Elderly in Nursing Homes")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/6766947"  # S1 Dataset.SAV

COV_MAP = {
    "Gender":    "cov_gender",     # 1/2
    "Age":       "cov_age",
    "Marriage":  "cov_marriage",
    "Education": "cov_education",
    "illness":   "cov_illness_count",
}

CESD_ITEMS  = [f"CES{i}" for i in range(1, 21)]
UCLA_ITEMS  = [f"UCLA{i}" for i in range(1, 9)]
RRS_ITEMS   = ["RRS1", "RRS2", "RRS4", "RRS5", "RRS6", "RRS7", "RRS8",
               "RRS9", "RRS10", "RRS11"]

SCALES = {
    "gan_2015_cesd":            (CESD_ITEMS, 0, 3),
    "gan_2015_ucla_loneliness": (UCLA_ITEMS, 1, 4),
    "gan_2015_rrs":             (RRS_ITEMS, 1, 3),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df, _meta = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    print("Downloading S1 Dataset.SAV …")
    df = fetch_data()

    df = df.rename(columns={"num": "id", **COV_MAP})
    assert df["id"].nunique() == len(df), "id column is not unique per row"
    df["id"] = df["id"].astype(int)
    cov_cols = list(COV_MAP.values())

    for out_name, (item_cols, lo, hi) in SCALES.items():
        keep = ["id"] + cov_cols + item_cols
        sub = df[keep].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)

        col_order = ["id", "item", "resp"] + cov_cols
        long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fname = f"{out_name}.csv"
        long.to_csv(OUT_DIR / fname, index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
