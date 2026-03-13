#!/usr/bin/env python3

import os
import pandas as pd

MKT_DATASETS = [
    ("osfstorage-archive (1)/2. Data/a. Original Data", "FS 3-5 MKT 2019.csv", 2019),
    ("osfstorage-archive/2. Data/a. Original Data", "FS 3-5 MKT 2020.csv", 2020),
    ("osfstorage-archive (1) 2/2. Data/a. Original Data", "FS 3-5 MKT 2021.csv", 2021),
    ("osfstorage-archive (2)/2. Data/a. Original Data", "FS 3-5 MKT 2022.csv", 2022),
]

OUT_COMBINED = "schoen_2019_to_2022_mkt.csv"


def _irw_columns(df):
    return df.rename(columns=lambda c: str(c).lower().replace(" ", "_").replace(".", "_"))


def convert_one(base, data_subdir, csv_name, year):
    orig_path = os.path.join(base, data_subdir, csv_name)
    if not os.path.isfile(orig_path):
        return None
    df = pd.read_csv(orig_path)
    df = _irw_columns(df)
    id_col = "publicid"
    cov_cols = [c for c in ["datacollectionwave"] if c in df.columns]
    item_cols = [c for c in df.columns if c != id_col and c not in cov_cols]

    out = df.melt(
        id_vars=[id_col] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    out = out.rename(columns={id_col: "id"})
    out["item"] = out["item"].astype(str).str.lower().str.replace(" ", "_")
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out.loc[out["resp"].isin([-99, 8]), "resp"] = pd.NA
    out["wave"] = year
    out = out.drop(columns=["datacollectionwave"], errors="ignore")
    extra = [c for c in out.columns if c not in ("id", "item", "resp")]
    out = out[["id", "item", "resp"] + extra]
    return out


def convert_mkt_to_irw():
    base = os.path.dirname(os.path.abspath(__file__))
    parts = []
    for data_subdir, csv_name, year in MKT_DATASETS:
        one = convert_one(base, data_subdir, csv_name, year)
        if one is not None:
            parts.append(one)
    if not parts:
        return
    combined = pd.concat(parts, ignore_index=True)
    out_path = os.path.join(base, OUT_COMBINED)
    combined.to_csv(out_path, index=False, na_rep="NA")
    print("  %s: rows=%d, items=%d, waves=%s" % (
        OUT_COMBINED, len(combined), combined["item"].nunique(),
        sorted(combined["wave"].unique())))
    return combined


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    print("Converting to IRW:")
    convert_mkt_to_irw()
