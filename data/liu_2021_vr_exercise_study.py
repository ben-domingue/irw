#!/usr/bin/env python3

import os
import re
import pandas as pd


INPUT_CSV = "complete data_IPD.csv"

OUTPUT_BREQ = "liu_2021_vrexp_breq.csv"
OUTPUT_BRUMS = "liu_2021_vrexp_brums.csv"
OUTPUT_DEPRESSION = "liu_2021_vrexp_depression.csv"
OUTPUT_READINESS = "liu_2021_vrexp_readiness.csv"
OUTPUT_GENERAL_OTHER = "liu_2021_vrexp_general_other.csv"


def _irw_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=lambda c: str(c).lower().replace(" ", "_").replace(".", "_"))


def _is_height_weight_or_pa(col: str) -> bool:
    n = col.lower()
    if n in ("pre_height", "post_height", "pre_weight", "post_weight"):
        return True
    if "perweekmins" in n or "sittingperweekhrs" in n:
        return True
    return False


def _melt_items(
    df: pd.DataFrame,
    id_col: str,
    cov_candidates: list[str],
    pre_cols: list[str],
    item_cols: list[str],
) -> pd.DataFrame | None:
    item_cols = [c for c in item_cols if c in df.columns]
    if not item_cols:
        return None
    out = pd.melt(
        df,
        id_vars=[id_col] + cov_candidates + pre_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    out = out.rename(columns={id_col: "id"})

    def pre_for_item(r):
        it = str(r["item"])
        if it.startswith("post_"):
            key = "pre_" + it[5:]
            if key in r.index:
                return r[key]
        return pd.NA

    out["itemcov_pretest"] = out.apply(pre_for_item, axis=1)
    out = out.drop(columns=[c for c in out.columns if c.startswith("pre_")], errors="ignore")
    out["itemcov_pretest"] = pd.to_numeric(out["itemcov_pretest"], errors="coerce")
    out = out.rename(columns={c: "cov_" + c for c in cov_candidates if c in out.columns and c != "id"})
    out["item"] = out["item"].astype(str).str.lower().str.replace(" ", "_")
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"])
    itemcov_cols = [c for c in out.columns if c.startswith("itemcov_")]
    cov_cols = [c for c in out.columns if c.startswith("cov_")]
    out = out[["id", "item", "resp"] + itemcov_cols + cov_cols]
    return _irw_columns(out)


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
    raw_item_cols = [c for c in df.columns if c not in [id_col] + cov_candidates + pre_cols]
    item_cols = [c for c in raw_item_cols if not _is_height_weight_or_pa(c)]

    breq = [c for c in item_cols if re.match(r"^post_breq_\d+$", c, re.I)]
    brums = [c for c in item_cols if re.match(r"^post_brums_\d+$", c, re.I)]
    depression = [c for c in item_cols if re.match(r"^post_depression_\d+$", c, re.I)]
    readiness = [c for c in item_cols if re.match(r"^readiness_\d+$", c, re.I)]
    split_set = set(breq + brums + depression + readiness)
    general_other = [c for c in item_cols if c not in split_set]

    outputs: list[tuple[str, list[str]]] = [
        (OUTPUT_BREQ, breq),
        (OUTPUT_BRUMS, brums),
        (OUTPUT_DEPRESSION, depression),
        (OUTPUT_READINESS, readiness),
        (OUTPUT_GENERAL_OTHER, general_other),
    ]

    written: list[pd.DataFrame] = []
    for fname, icols in outputs:
        part = _melt_items(df, id_col, cov_candidates, pre_cols, icols)
        path = os.path.join(base, fname)
        if part is None or part.empty:
            print(f"{fname}: skipped (no columns or empty)")
            continue
        part.to_csv(path, index=False)
        written.append(part)
        print(
            f"{fname}: rows={len(part)}, ids={part['id'].nunique()}, items={part['item'].nunique()}"
        )

    return written[0] if written else None


if __name__ == "__main__":
    convert_vr_exercise_to_irw()
