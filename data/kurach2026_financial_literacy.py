from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

DOI   = "10.7910/DVN/8XGUZI"
TITLE = "Financial literacy under intrinsic and extrinsic motivation"
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_ID = 13322526  # data.csv; semicolon-delimited

ITEM_COLS = ["Q1", "Q2", "Q3"]  # 0=incorrect, 1=correct, 2=don't know


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep=";")


def convert():
    print("Downloading data.csv …")
    raw = fetch_data()

    cov = raw[["obs", "gender", "treatment", "total_time"]].rename(columns={
        "obs": "id",
        "gender": "cov_gender",
        "treatment": "cov_treatment",
        "total_time": "cov_total_time",
    })
    cov["cov_total_time"] = cov["cov_total_time"].astype(str).str.replace(",", ".").astype(float)

    items = raw[["obs"] + ITEM_COLS].rename(columns={"obs": "id"})
    long = items.merge(cov, on="id").melt(
        id_vars=["id", "cov_gender", "cov_treatment", "cov_total_time"],
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    # raw code 2 = "don't know" — a non-response, not a third ordinal step
    # above "correct"; only 0 (incorrect) / 1 (correct) form a valid ordinal
    # pair. dropna() alone would not catch this since 2 is a real number.
    long = long[long["resp"].isin([0, 1])].reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cov_gender", "cov_treatment", "cov_total_time"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "kurach2026_financial_literacy.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
