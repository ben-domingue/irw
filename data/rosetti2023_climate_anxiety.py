from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE    = "Climate Anxiety Data Base"
URL      = "https://figshare.com/articles/dataset/Climate_Anxiety_Data_Base/16900393"
UA       = {"User-Agent": "irw-batch/1.0 (research)"}
FILE_URL = "https://ndownloader.figshare.com/files/40839032"

COV_COLS = {
    "age": "cov_age",
    "gender": "cov_gender",
    "t.soc.net": "cov_social_net_time",
    "t.news": "cov_news_time",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


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
    print("Downloading ClimateAnxietyDataBase.csv …")
    raw = fetch_data()

    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    gad7_cols = [f"GAD7_q{i}" for i in range(1, 8)]
    cas_cols = [f"CAS_q{i}" for i in range(1, 23)]
    cckq_cols = [f"CCKQ_q{i}" for i in range(1, 11)]

    gad7 = _melt_scale(raw, gad7_cols, cov)
    write_scale(gad7, "rosetti2023_gad7.csv")

    cas = _melt_scale(raw, cas_cols, cov)
    write_scale(cas, "rosetti2023_climate_anxiety.csv")

    # CCKQ items are "correct"/"incorrect" strings -> binary 1/0
    cckq_raw = raw.copy()
    cckq_raw[cckq_cols] = cckq_raw[cckq_cols].replace({"correct": 1, "incorrect": 0})
    cckq = _melt_scale(cckq_raw, cckq_cols, cov)
    write_scale(cckq, "rosetti2023_climate_knowledge.csv")


if __name__ == "__main__":
    convert()
