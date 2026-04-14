#!/usr/bin/env python3

import os

import pandas as pd


INPUT_CSV = "pone.0345773.s001.csv"
OUTPUT_CSV = "stait_trait_anxiety_irw.csv"


def convert_to_irw():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, INPUT_CSV)
    if not os.path.isfile(path):
        print(f"Missing {path}")
        return None

    df = pd.read_csv(path)
    if df.empty:
        print("Input is empty.")
        return None

    sex_col = "sex"
    if sex_col not in df.columns:
        print("Expected column 'sex' not found.")
        return None

    item_cols = [c for c in df.columns if c.startswith("STAI_State_") or c.startswith("STAI_Trait_")]
    item_cols = [
        c
        for c in item_cols
        if c not in ("STAI_State_total", "STAI_Trait_total")
    ]
    dup_raw = {
        "STAI_State_1",
        "STAI_State_2",
        "STAI_State_5",
        "STAI_State_8",
        "STAI_State_10",
        "STAI_State_11",
        "STAI_State_15",
        "STAI_State_16",
        "STAI_State_19",
        "STAI_State_20",
        "STAI_Trait_1r",
        "STAI_Trait_6r",
        "STAI_Trait_7r",
        "STAI_Trait_10r",
        "STAI_Trait_13r",
        "STAI_Trait_16r",
        "STAI_Trait_19r",
    }
    item_cols = [c for c in item_cols if c not in dup_raw]

    df = df.rename(columns={"sex": "cov_sex"})
    df["id"] = range(1, len(df) + 1)

    out = pd.melt(
        df,
        id_vars=["id", "cov_sex"],
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    out["item"] = out["item"].astype(str).str.lower()
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"])
    out = out[["id", "item", "resp", "cov_sex"]].sort_values(["id", "item"]).reset_index(drop=True)

    out_path = os.path.join(base, OUTPUT_CSV)
    out.to_csv(out_path, index=False)
    print(f"{OUTPUT_CSV}: rows={len(out)} ids={out['id'].nunique()} items={out['item'].nunique()}")
    return out


if __name__ == "__main__":
    convert_to_irw()
