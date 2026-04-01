#!/usr/bin/env python3

import os
import pandas as pd


INPUT_SAV = "osfstorage-archive (3)/Data_Family functioning dental students Latin America.sav"
OUTPUT_CSV = "dental_students_faces_latin_america_irw.csv"


def convert_dental_students_to_irw():
    base = os.path.dirname(os.path.abspath(__file__))
    in_path = os.path.join(base, INPUT_SAV)
    if not os.path.isfile(in_path):
        print(f"Input file not found at {in_path}")
        return None

    df = pd.read_spss(in_path, convert_categoricals=True)
    if df.empty:
        print("Input file is empty.")
        return None

    df = df.rename(columns={"ID": "id"})
    for c in ["Country", "University", "Study", "Sex"]:
        if c in df.columns:
            df = df.rename(columns={c: "cov_" + c.lower()})

    item_cols = [c for c in df.columns if c in [
        "P1c", "P2a", "P3a", "P4c", "P5c", "P6a", "P7a", "P8c", "P9a", "P10c",
        "P11c", "P12a", "P13c", "P14a", "P15c", "P16a", "P17c", "P18a", "P19c", "P20",
    ]]
    cov_cols = [c for c in df.columns if c.startswith("cov_")]
    df = df[["id"] + cov_cols + item_cols]

    out = pd.melt(
        df,
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )

    out["item"] = out["item"].astype(str)
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"])
    cov_cols_final = [c for c in out.columns if c.startswith("cov_")]
    out = out[["id", "item", "resp"] + cov_cols_final]
    out = out.sort_values(["id", "item"]).reset_index(drop=True)

    out_path = os.path.join(base, OUTPUT_CSV)
    out.to_csv(out_path, index=False)
    print(f"{OUTPUT_CSV}: rows={len(out)}, ids={out['id'].nunique()}, items={out['item'].nunique()}")
    return out


if __name__ == "__main__":
    convert_dental_students_to_irw()
