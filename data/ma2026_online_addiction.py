from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Assessing Online-Related Addiction in Chinese Primary School "
         "Students: An Item Response Theory Analysis of Three Scales "
         "(Ma, An, Chen & Liu, 2026, Research Square preprint)")
URL  = "https://figshare.com/articles/dataset/Assessing_Online-Related_Addiction_in_Chinese_Primary_School_Students_An_Item_Response_Theory_Analysis_of_Three_Scales/27211839"
DOI  = "10.21203/rs.3.rs-9429022/v1"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/49748748"

# birthdate is PII (date of birth for primary-school-aged children) -- dropped
# entirely, not just deprioritized. Assess_Date is kept as a raw covariate
# despite mixed formatting (some rows "YYYYMMDD" strings, some Excel date
# serials) -- not identifying on its own once birthdate is gone.
COV_COLS = {
    "Sex": "cov_sex",
    "Grade": "cov_grade",
    "Race": "cov_race",
    "Sick": "cov_sick",
    "Assess_Date": "cov_assess_date",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def _melt_scale(raw: pd.DataFrame, item_cols: list[str], cov: pd.DataFrame,
                 valid_max: int | None = None) -> pd.DataFrame:
    items = raw[["id"] + item_cols]
    cov_cols = list(cov.columns.drop("id"))
    long = items.merge(cov, on="id").melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    if valid_max is not None:
        long = long[long["resp"] <= valid_max]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    return long[col_order].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


def convert():
    print("Downloading rawdata_.csv ...")
    raw = fetch_data()
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    # BSMAS (Bergen Social Media Addiction Scale), 6 items, 1-5 Likert
    bsmas_cols = [f"bsmas{i}" for i in range(1, 7)]
    write_scale(_melt_scale(raw, bsmas_cols, cov), "ma2026_bsmas.csv")

    # SABAS (Smartphone Application-Based Addiction Scale), 6 items, 1-6 Likert
    sabas_cols = [f"sabas{i}" for i in range(1, 7)]
    write_scale(_melt_scale(raw, sabas_cols, cov), "ma2026_sabas.csv")

    # IGDS9-SF (Internet Gaming Disorder Scale-Short Form), 9 items, 1-5
    # Likert. One stray value of 6 in the raw file (single cell, igds9) is
    # outside the documented 1-5 range -- filtered as a data-entry error.
    igds_cols = [f"igds{i}" for i in range(1, 10)]
    write_scale(_melt_scale(raw, igds_cols, cov, valid_max=5), "ma2026_igds.csv")


if __name__ == "__main__":
    convert()
