from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE    = ("Assessing psychological flexibility: The psychometric "
            "properties of the Czech translation of the CompACT "
            "questionnaire")
URL      = "https://osf.io/cwjxq/"
UA       = {"User-Agent": "irw-batch/1.0 (research)"}
FILE_URL = "https://osf.io/download/zs27k/"

GENDER_MAP = {"zena": "female", "muz": "male", "jine": "other"}

COV_COLS = {
    "Pohlavi": "cov_gender",
    "Vek":     "cov_age",
}

COMPACT_COLS = ["VA1", "OE2R", "BA3R", "OE4R", "VA5", "OE6R", "VA7", "OE8R",
                "BA9R", "VA10", "OE11R", "BA12R", "OE13", "VA14", "OE15R",
                "BA16R", "VA17", "OE18R", "BA19R", "OE20", "VA21", "OE22",
                "VA23"]
DASS21_COLS = ["S1", "A2", "D3", "A4", "D5", "S6", "A7", "S8", "A9", "D10",
               "S11", "S12", "D13", "S14", "A15", "D16", "D17", "S18", "A19",
               "A20", "D21"]
AAQ2_COLS = [f"AAQ{i}" for i in range(1, 8)]
SWLS_COLS = [f"SWL{i}" for i in range(1, 6)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df["id"] = df["ID"]
    df["Pohlavi"] = df["Pohlavi"].map(GENDER_MAP)
    return df


def _melt_scale(raw: pd.DataFrame, item_cols: list[str], cov: pd.DataFrame) -> pd.DataFrame:
    items = raw[["id"] + item_cols]
    long = items.merge(cov, on="id").melt(
        id_vars=["id"] + list(cov.columns.drop("id")),
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + list(cov.columns.drop("id"))
    return long[col_order].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


def convert():
    print("Downloading CompACT(CZ) Dataset.csv …")
    raw = fetch_data()

    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    compact = _melt_scale(raw, COMPACT_COLS, cov)
    write_scale(compact, "ptacek2023_compact.csv")

    dass21 = _melt_scale(raw, DASS21_COLS, cov)
    write_scale(dass21, "ptacek2023_dass21.csv")

    aaq2 = _melt_scale(raw, AAQ2_COLS, cov)
    write_scale(aaq2, "ptacek2023_aaq2.csv")

    swls = _melt_scale(raw, SWLS_COLS, cov)
    write_scale(swls, "ptacek2023_swls.csv")


if __name__ == "__main__":
    convert()
