from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = "Polish Adaptation of the Online Test Anxiety Inventory (OTAI)"
URL   = "https://osf.io/r67wb/"
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://osf.io/download/qmyfb/"  # OTAI_retest_dane.csv; semicolon-delimited

ITEM_COLS = [f"OTAI_{i}" for i in range(1, 19)]  # 18 items, 0-3 Likert


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep=";")


def convert():
    print("Downloading OTAI_retest_dane.csv …")
    raw = fetch_data()

    # Source `id` column has one collision (two respondents share id=10078,
    # timestamps a minute apart — a data-entry coincidence, not a real retest
    # pair); use row position as id instead.
    raw = raw.reset_index(drop=True)
    raw["id"] = raw.index

    cov = raw[["id", "Wiek", "Plec_sl", "Duration (in seconds)"]].rename(columns={
        "Wiek": "cov_age",
        "Plec_sl": "cov_gender",  # numeric code: 1=Kobieta (female), 2=Mezczyzna (male)
        "Duration (in seconds)": "cov_duration_seconds",
    })

    items = raw[["id"] + ITEM_COLS]
    long = items.merge(cov, on="id").melt(
        id_vars=["id", "cov_age", "cov_gender", "cov_duration_seconds"],
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cov_age", "cov_gender", "cov_duration_seconds"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "schoepp2022_test_anxiety.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
