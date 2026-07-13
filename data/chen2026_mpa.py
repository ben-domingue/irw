from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

DOI   = "10.7910/DVN/QS5D8C"
TITLE = ("A linkage of college students' mobile phone addiction and social "
         "anxiety: The mediating role of self-control")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_ID = 13969898  # MobilePhoneAddiction-Self-Control.xls.xlsx

COV_COLS = {
    "1.Gender":                        "cov_gender",
    "2.Grade":                         "cov_grade",
    "3.Major":                         "cov_major",
    "4.Only-child":                    "cov_only_child",
    "5.Household registration type":   "cov_household_registration",
}


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    # Source '序号' (row number) column has 27 duplicate values — a data-entry
    # artifact, not a repeated-measures id — so use row position instead.
    df["id"] = df.index
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
    print("Downloading MobilePhoneAddiction-Self-Control.xls.xlsx …")
    raw = fetch_data()

    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    mpa_cols = [c for c in raw.columns if c.startswith("6.MPA")]
    sa_cols  = [c for c in raw.columns if c.startswith("7.SA")]
    sc_cols  = [c for c in raw.columns if c.startswith("8.SC")]

    mpa = _melt_scale(raw, mpa_cols, cov)
    write_scale(mpa, "chen2026_mpa.csv")

    sa = _melt_scale(raw, sa_cols, cov)
    write_scale(sa, "chen2026_sa.csv")

    sc = _melt_scale(raw, sc_cols, cov)
    write_scale(sc, "chen2026_sc.csv")


if __name__ == "__main__":
    convert()
