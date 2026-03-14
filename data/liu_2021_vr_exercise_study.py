#!/usr/bin/env python3

import os
import pandas as pd


INPUT_CSV = "complete data_IPD.csv"
OUTPUT_CSV = "liu_2021_vr_exercise_study.csv"


def _irw_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=lambda c: str(c).lower().replace(" ", "_").replace(".", "_"))


def convert_vr_exercise_to_irw():
    base = os.path.dirname(os.path.abspath(__file__))
    in_path = os.path.join(base, INPUT_CSV)
    if not os.path.isfile(in_path):
        print(f"Input CSV not found at {in_path}")
        return None

    df = pd.read_csv(in_path)
    if df.empty:
        print("Input CSV is empty.")
        return None

    df = _irw_columns(df)

    derived_cols = [
        "pre_height_meter",
        "post_height_meter",
        "pre_bmi",
        "post_bmi",
        "pre_amotivation",
        "pre_externalregulation",
        "pre_introjectedregulation",
        "pre_identifiedregulation",
        "pre_intrinsicregulation",
        "post_amotivation",
        "post_externalregulation",
        "post_introjectedregulation",
        "post_identifiedregulation",
        "post_intrinsicregulation",
        "pre_anger",
        "pre_confusion",
        "pre_depression",
        "pre_fatigue",
        "pre_tension",
        "pre_vigor",
        "post_anger",
        "post_confusion",
        "post_depression",
        "post_fatigue",
        "post_tension",
        "post_vigor",
        "pre_depressionscore",
        "pre_dpscore",
        "post_depressionscore",
        "post_dpscore",
        "pre_pa",
        "post_pa",
    ]
    df = df.drop(columns=[c for c in derived_cols if c in df.columns], errors="ignore")

    cols = list(df.columns)
    id_col = "id" if "id" in cols else None
    if id_col is None:
        df["id"] = range(1, len(df) + 1)
        id_col = "id"

    cov_candidates = [c for c in ["group", "gender", "age", "raceethnicity"] if c in cols]
    pre_cols = [c for c in df.columns if c.startswith("pre_")]
    item_cols = [c for c in df.columns if c not in [id_col] + cov_candidates + pre_cols]
    if not item_cols:
        print("No item columns found to convert.")
        return None

    out = pd.melt(
        df,
        id_vars=[id_col] + cov_candidates + pre_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )

    out = out.rename(columns={id_col: "id"})
    out["itemcov_pretest"] = out.apply(
        lambda r: r["pre_" + r["item"][5:]] if r["item"].startswith("post_") and "pre_" + r["item"][5:] in r else pd.NA,
        axis=1,
    )
    out = out.drop(columns=[c for c in out.columns if c.startswith("pre_")], errors="ignore")
    out["itemcov_pretest"] = pd.to_numeric(out["itemcov_pretest"], errors="coerce")
    out = out.rename(columns={c: "cov_" + c for c in cov_candidates if c in out.columns and c != "id"})

    out["item"] = out["item"].astype(str).str.lower().str.replace(" ", "_")
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"])

    itemcov_cols = [c for c in out.columns if c.startswith("itemcov_")]
    cov_cols = [c for c in out.columns if c.startswith("cov_")]
    out = out[["id", "item", "resp"] + itemcov_cols + cov_cols]
    out = _irw_columns(out)

    out_path = os.path.join(base, OUTPUT_CSV)
    out.to_csv(out_path, index=False)

    print(f"{OUTPUT_CSV}: rows={len(out)}, ids={out['id'].nunique()}, items={out['item'].nunique()}")
    return out


if __name__ == "__main__":
    convert_vr_exercise_to_irw()

