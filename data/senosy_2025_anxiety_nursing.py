#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/30693638
# DOI: 10.6084/m9.figshare.30693638.v2
# Download raw file: https://ndownloader.figshare.com/files/59998088 -> Data.xlsx
# STAI-Y State (20 items) and Trait (20 items) for undergraduate nursing students (Egypt).
# Scale scored 1-4; "STA-Y" and "TAI-Y" columns are total scores, excluded.

import os
import pandas as pd

BASE    = os.path.dirname(os.path.abspath(__file__))
RAW     = os.path.join(BASE, "Data.xlsx")
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output", "cleaned")

COV_COLS = {
    "Age":                                          "cov_age",
    "Gender ":                                      "cov_gender",
    "University entrance average score is ":        "cov_entrance_score",
    "Is this the second time for that year (Level)?": "cov_repeat_year",
    "Marital Status:":                              "cov_marital_status",
    "Do you work and study?":                       "cov_work_study",
}

# Columns that are total scores, not items
SKIP = {"STA-Y", "TAI-Y"}


def _split_state_trait(df):
    """Split columns into state (before TAI-Y) and trait (after TAI-Y)."""
    cols = list(df.columns)
    try:
        state_start = cols.index("STA-Y") + 1
        trait_start = cols.index("TAI-Y") + 1
        state_cols = cols[state_start:cols.index("TAI-Y")]
        trait_cols = cols[trait_start:]
    except ValueError:
        # Fallback: first 20 item-like cols = state, next 20 = trait
        item_cols = [c for c in cols if c not in SKIP and not c.startswith(
            ("ID", "Age", "Gender", "University", "Is this", "Marital", "Kind", "Do you"))]
        state_cols, trait_cols = item_cols[:20], item_cols[20:40]
    return state_cols, trait_cols


def convert():
    df = pd.read_excel(RAW)
    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    cov_rename = {k: v for k, v in COV_COLS.items() if k in df.columns}
    df = df.rename(columns=cov_rename)
    cov_present = [v for v in COV_COLS.values() if v in df.columns]

    state_cols, trait_cols = _split_state_trait(df)

    for out_name, item_cols in [
        ("senosy_2025_anxiety_state", state_cols),
        ("senosy_2025_anxiety_trait", trait_cols),
    ]:
        item_cols = [c for c in item_cols if c not in SKIP]
        long = df.melt(id_vars=["id"] + cov_present, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["item"] = long["item"].str.strip()
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_present]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
