from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("The way aesthetic needs affects the relationship between "
         "aesthetic responsiveness and creativity (Dou, Zhang, Wang, Zhang "
         "& Hou, 2025, PLOS ONE)")
URL  = "https://plos.figshare.com/articles/dataset/_/30033097"
DOI  = "10.1371/journal.pone.0331067"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/57597382"

# Three named instruments in one wide sheet, separated in the source file by
# blank "Unnamed" gap columns -- that gap lines up exactly with the paper's
# 3 tools: Aesthetic Needs Scale (ANS), Aesthetic Responsiveness Assessment
# (AReA, includes a few creative-behaviour items e.g. "sculpt/paint/write
# poetry/took an art class"), and the Williams Creative Tendency Scale
# (WCTS). Column positions confirmed by direct inspection, not guessed from
# question numbering alone.
ID_COL = "序号"
COV_COLS = {
    "1、您的性别：": "cov_gender",
    "2、您的年龄段：": "cov_age_band",
    "3、1. 您的学科为": "cov_field",
    "4、受教育程度": "cov_education",
    "5、您的职业": "cov_occupation",
    "6、您的收入": "cov_income",
}

# (table name, column slice start, column slice end, valid_min, valid_max)
# Slices are positional against the raw column list; valid_max confirmed
# per-item -- one AReA item ("28...") had 6 junk decimal values (9.6-87.1)
# that only occur on the same 14 rows where id is NaN (trailing
# formula/summary rows at the bottom of the sheet, not real respondents);
# dropping those rows before melting removes them, and 748 unique ids remain
# afterward -- matching the paper's reported N=748 exactly.
SCALES = {
    "dou2025_ans":  (8, 26, 1, 6),
    "dou2025_area": (27, 39, 1, 5),
    "dou2025_wcts": (40, 63, 1, 5),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content))


def write_scale(raw: pd.DataFrame, prefix: str, start: int, end: int,
                 valid_min: int, valid_max: int, cov: pd.DataFrame, fname: str):
    cov_cols = list(cov.columns.drop("id"))
    item_cols = list(raw.columns[start:end])
    items = raw[["id"] + item_cols].merge(cov, on="id")
    long = items.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["item"] = [f"{prefix}_{i+1}" for i in
                     (long["item"].map({c: n for n, c in enumerate(item_cols)}))]
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= valid_min) & (long["resp"] <= valid_max)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


def convert():
    print("Downloading pone.0331067.s001.xlsx ...")
    raw = fetch_data()
    raw = raw.rename(columns={ID_COL: "id"})
    # Trailing rows with no id are sheet-bottom junk (formula/summary
    # artifacts, not respondents) -- dropping them recovers exactly the
    # paper's reported N=748.
    raw = raw.dropna(subset=["id"]).reset_index(drop=True)
    raw["id"] = raw["id"].astype(int)
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    for table, (start, end, valid_min, valid_max) in SCALES.items():
        write_scale(raw, table.replace("dou2025_", ""), start, end,
                    valid_min, valid_max, cov, f"{table}.csv")


if __name__ == "__main__":
    convert()
