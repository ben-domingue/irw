#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331560
# DOI: 10.1371/journal.pone.0331560
# SI: S1 Data (10.1371/journal.pone.0331560.s001), XLSX
#
# 16-item teacher-leadership self-assessment, text-coded 5-point Likert.
# Paper's Methods text (section 3.2): "5 representing complete compliance,
# 4 representing relatively compliance, 3 representing basic compliance,
# 2 representing basic non-compliance, and 1 representing complete
# non-compliance."

import os
import io
import re
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0331560.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

RESP_MAP = {
    "complete non-compliance": 1,
    "basic non-compliance": 2,
    "basic compliance": 3,
    "relatively compliance": 4,
    "complete compliance": 5,
}

COV_MAP = {
    "Gender": "cov_gender",
    "Ethnicity": "cov_ethnicity",
    "Age": "cov_age",
    "Teaching Experience": "cov_teaching_experience",
    "Major studied": "cov_major",
    "Graduated from Normal University": "cov_normal_university_grad",
    "Education": "cov_education",
    "Professional Title": "cov_professional_title",
    "Educational Stage": "cov_educational_stage",
    "Region": "cov_region",
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")

    df = df.rename(columns={"number": "id"})
    df = df.rename(columns=COV_MAP)
    assert df["id"].nunique() == len(df)

    item_cols = [c for c in df.columns if re.match(r"^\d+\.", c)]
    item_names = {c: f"item_{i+1}" for i, c in enumerate(item_cols)}
    df = df.rename(columns=item_names)
    item_col_names = list(item_names.values())

    cov_cols = list(COV_MAP.values())
    long = df[["id"] + cov_cols + item_col_names].melt(
        id_vars=["id"] + cov_cols, value_vars=item_col_names,
        var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(str).str.strip().str.lower().map(RESP_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "dong_2025_teacher_leadership.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
