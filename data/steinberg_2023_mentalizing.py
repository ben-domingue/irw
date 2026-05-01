#!/usr/bin/env python3

import os
import pandas as pd

RAW_MOMENTARY = "Steinberg_DailyMz_Momentary_Data.csv"
RAW_BASELINE = "Steinberg_DailyMz_Lab_Baseline_Data.csv"
OUT_MOMENTARY = "steinberg_2023_mentalizing_momentary.csv"

RAW_ITEM_COLS_MOMENTARY = ["mentsotherema", "mentsselfema", "rfema"]


def _irw_columns(df):
    return df.rename(columns=lambda c: str(c).lower().replace(" ", "_").replace(".", "_"))


def _find_raw_csv(base, name):
    for sub in ["", "Data and Codebook", "steinberg_2023_mentalizing"]:
        p = os.path.join(base, sub, name)
        if os.path.isfile(p):
            return p
    return None


def convert_momentary_to_irw(df):
    df = df.copy()
    df = _irw_columns(df)
    if "participant_id" in df.columns:
        df = df.rename(columns={"participant_id": "id"})
    id_col = "id"
    day_col = "day"
    if day_col not in df.columns:
        day_col = None
    keep_items = [c for c in RAW_ITEM_COLS_MOMENTARY if c in df.columns]
    if not keep_items:
        keep_items = [c for c in df.columns if c not in (id_col, "day", "surveyid", "surveyidoverall")
                       and "mean" not in c.lower()]
    out = df.melt(
        id_vars=[id_col] + ([day_col] if day_col else []),
        value_vars=keep_items,
        var_name="item",
        value_name="resp",
    )
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"])
    out["item"] = out["item"].astype(str).str.lower().str.replace(" ", "_").str.replace(".", "_")
    if day_col:
        out = out.rename(columns={day_col: "wave"})
    cols = [id_col, "item", "resp"]
    if "wave" in out.columns:
        cols.append("wave")
    out = out[[c for c in cols if c in out.columns]]
    return _irw_columns(out)


def convert_mentalizing_to_irw():
    base = os.path.dirname(os.path.abspath(__file__))
    momentary_path = _find_raw_csv(base, RAW_MOMENTARY)
    if momentary_path is None:
        print("Mentalizing: %s not found in folder or Data and Codebook/." % RAW_MOMENTARY)
        return None

    df_momentary = pd.read_csv(momentary_path)
    out_momentary = convert_momentary_to_irw(df_momentary)
    out_path = os.path.join(base, OUT_MOMENTARY)
    out_momentary.to_csv(out_path, index=False)
    print("Momentary ->", out_path)
    print("  Rows:", len(out_momentary), "| Participants:", out_momentary["id"].nunique(), "| Items:", out_momentary["item"].nunique())
    print("  (Baseline omitted: contains only subscale/total scores, not raw item-level data.)")
    return out_momentary


if __name__ == "__main__":
    convert_mentalizing_to_irw()
