from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

DOI   = "10.7910/DVN/UOBDRV"
TITLE = "gender differences in motivation PNS and academic achievement"
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_ID = 7590042  # source files308.xlsx

# Column indices (0-based) after skipping 2 header rows
# Row 0: group labels (PE-ACRS at 6, PE-MS at 21)
# Row 1: cov cols (0-5), item numbers (6-17, 21-29), subscale sums (18-20, 30-32)
COV_COLS = {
    0: "cov_gender",      # 1=male, 2=female
    1: "cov_age",
    2: "cov_bmi",
    3: "cov_university",  # 1=KFU, 2=TU, 3=KSU
    4: "cov_elearning_experience",
    5: "cov_gpa",
}

PE_ACRS_COLS = list(range(6, 18))    # items 1-12
PE_MS_COLS   = list(range(21, 30))   # items 13-21
DROP_COLS    = list(range(18, 21)) + list(range(30, 33))  # subscale sums


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    # Two header rows: row 0 = group labels, row 1 = column names/numbers
    df = pd.read_excel(io.BytesIO(r.content), header=None, skiprows=2)
    return df


def build_long(df: pd.DataFrame, item_col_indices: list[int], item_prefix: str,
               cov_df: pd.DataFrame) -> pd.DataFrame:
    item_df = df.iloc[:, item_col_indices].copy()
    # Use original item numbers from row 1 (already stripped from header)
    item_numbers = [df.columns[i] if isinstance(df.columns[i], int) else i
                    for i in item_col_indices]
    item_df.columns = [f"{item_prefix}{n}" for n in range(1, len(item_col_indices) + 1)]

    item_df["id"] = df.index
    cov_df = cov_df.copy()
    cov_df["id"] = df.index

    merged = item_df.merge(cov_df, on="id")
    item_names = [c for c in item_df.columns if c != "id"]
    cov_names  = [c for c in cov_df.columns  if c != "id"]

    long = merged[["id"] + cov_names + item_names].melt(
        id_vars=["id"] + cov_names,
        value_vars=item_names,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_names
    return long[col_order].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")


def convert():
    print("Downloading source files308.xlsx …")
    raw = fetch_data()

    # Drop completely empty rows
    raw = raw.dropna(how="all").reset_index(drop=True)

    cov_df = raw.iloc[:, list(COV_COLS.keys())].copy()
    cov_df.columns = list(COV_COLS.values())

    acrs = build_long(raw, PE_ACRS_COLS, "q", cov_df)
    # Relabel items q1-q12 (already numbered 1-12)
    ms = build_long(raw, PE_MS_COLS, "q", cov_df)
    # Relabel PE-MS items as q13-q21 to match original numbering
    ms_item_map = {f"q{i}": f"q{i+12}" for i in range(1, 10)}
    ms["item"] = ms["item"].map(ms_item_map)

    write_scale(acrs, "frikha_2023_pe_acrs.csv")
    write_scale(ms,   "frikha_2023_pe_ms.csv")


if __name__ == "__main__":
    convert()
