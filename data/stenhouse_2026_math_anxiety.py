#!/usr/bin/env python3
# Source: https://e-space.mmu.ac.uk/id/eprint/644376
# DOI: 10.23634/mmu.00644376
# Download raw file: https://e-space.mmu.ac.uk/644376/1/Survey%20Complete%20Data%20%20.xlsx
# Trainee teachers in England: math anxiety (1-item), math teaching anxiety scale (19 items),
# and math confidence (6 items). Teaching anxiety items coded as text ("1 - Never" etc.).

import os
import re
import pandas as pd

BASE    = os.path.dirname(os.path.abspath(__file__))
RAW     = os.path.join(BASE, "Survey Complete Data  .xlsx")
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output", "cleaned")

TEACHING_ANXIETY_PREFIX = "18."
CONFIDENCE_PREFIX = "15."
MATH_ANXIETY_COL   = "17.1. How maths-anxious are you?"
TEACH_ANXIETY_COL  = "20.1. How anxious are you when teaching maths?"


def _parse_text_resp(series):
    """Extract leading integer from coded responses like '3 - Sometimes'."""
    def _extract(val):
        if pd.isna(val):
            return float("nan")
        m = re.match(r"(\d+)", str(val).strip())
        return int(m.group(1)) if m else float("nan")
    return series.map(_extract)


def convert():
    df = pd.read_excel(RAW)
    id_col = df.columns[0]
    df = df.rename(columns={id_col: "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    gender_col = next((c for c in df.columns if c.startswith("11.")), None)
    age_col    = next((c for c in df.columns if c.startswith("12.")), None)
    cov_map = {}
    if gender_col:
        cov_map[gender_col] = "cov_gender"
    if age_col:
        cov_map[age_col] = "cov_age"
    df = df.rename(columns=cov_map)
    cov_present = list(cov_map.values())

    # Math teaching anxiety scale (Hunt & Sari, 2019): items 18.1-18.19, 5-point text-coded
    ta_cols = [c for c in df.columns if str(c).startswith(TEACHING_ANXIETY_PREFIX)]
    for c in ta_cols:
        df[c] = _parse_text_resp(df[c])

    # Math confidence: items 15.1-15.6, 5-point text-coded
    conf_cols = [c for c in df.columns if str(c).startswith(CONFIDENCE_PREFIX)]
    for c in conf_cols:
        df[c] = _parse_text_resp(df[c])

    # Melt all item groups into long format then concatenate into one table
    parts = []
    for item_cols in [ta_cols, conf_cols]:
        long = df.melt(id_vars=["id"] + cov_present, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        parts.append(long)

    for col in [MATH_ANXIETY_COL, TEACH_ANXIETY_COL]:
        if col not in df.columns:
            continue
        sub = df[["id"] + cov_present + [col]].copy()
        sub[col] = pd.to_numeric(sub[col], errors="coerce")
        sub = sub.rename(columns={col: "resp"})
        sub["item"] = col
        parts.append(sub[["id"] + cov_present + ["item", "resp"]])

    combined = pd.concat(parts, ignore_index=True)
    combined = combined.dropna(subset=["resp"]).reset_index(drop=True)
    combined = combined[["id", "item", "resp"] + cov_present]

    path = os.path.join(OUT_DIR, "stenhouse_2026_math_anxiety.csv")
    combined.to_csv(path, index=False)
    print(f"stenhouse_2026_math_anxiety.csv: rows={len(combined)} ids={combined['id'].nunique()} "
          f"items={combined['item'].nunique()} resp={combined['resp'].min():.0f}-{combined['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
