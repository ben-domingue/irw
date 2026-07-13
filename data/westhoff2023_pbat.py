from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE    = ("Stop Being So Rigid: The Interplay of Psychological "
            "Flexibility and Cognitive-Affective Processes in the Daily "
            "Lives of Young Adults")
URL      = "https://osf.io/ejtzs/"
UA       = {"User-Agent": "irw-batch/1.0 (research)"}
FILE_URL = "https://osf.io/download/aq569/"

COV_COLS = {
    "Gender": "cov_gender",
    "Age":    "cov_age",
}

PBAT_COLS  = [f"PBAT-{i}" for i in range(1, 19)]
STOPD_COLS = [f"STOPD-{i}" for i in range(1, 6)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df["id"] = df["VID"].astype(int)
    # -1 marks an unfinished/unanswered ESM session (all items -1 together);
    # not a point on the 0-100 continuous scale, so drop those rows entirely.
    df = df[df["Finished"] != -1].reset_index(drop=True)
    # Sequential within-person timepoint: up to 21 days x 5 sessions/day.
    df["wave"] = (df["Day"].astype(int) - 1) * 5 + df["Session"].astype(int)
    return df


def _melt_scale(raw: pd.DataFrame, item_cols: list[str], cov: pd.DataFrame) -> pd.DataFrame:
    items = raw[["id", "wave"] + item_cols]
    long = items.merge(cov, on="id").melt(
        id_vars=["id", "wave"] + list(cov.columns.drop("id")),
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    col_order = ["id", "item", "resp", "wave"] + list(cov.columns.drop("id"))
    return long[col_order].sort_values(["id", "wave", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} rows={len(long)}")


def convert():
    print("Downloading Network Analysis Psychological Flexibility_Data.csv …")
    raw = fetch_data()

    cov = raw[["id"] + list(COV_COLS.keys())].drop_duplicates(subset=["id"]).rename(columns=COV_COLS)

    pbat = _melt_scale(raw, PBAT_COLS, cov)
    write_scale(pbat, "westhoff2023_pbat.csv")

    stopd = _melt_scale(raw, STOPD_COLS, cov)
    write_scale(stopd, "westhoff2023_stopd.csv")


if __name__ == "__main__":
    convert()
