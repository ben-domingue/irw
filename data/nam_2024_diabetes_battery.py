#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0299971
# DOI: 10.1371/journal.pone.0299971
# Supporting Information (S1 Data, "Raw_Data" sheet):
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0299971.s001
#
# Nam & Yoon (2024), "Pathways linking health literacy to self-care in
# diabetic patients with physical disabilities". Single sample, N=214, no
# missing data ("Of 214 survey results, none had missing data or numerical
# outliers"). Seven distinct instruments in one raw-data sheet -> seven
# output tables, one per scale (datastandard.md "one scale per file"):
#
#   khlat     KHLAT-4 health-literacy word-recognition test, 66 items, 1-4
#             (raw per-item familiarity rating; the paper's 0-66 total score
#             is a post-hoc dichotomization of this raw item -- not shipped)
#   selfcare  Diabetes Self-care Scale, 15 items, 1-4
#   access    Health Navigation Self-sufficiency Scale, 10 items, 0-1
#   medint    Medical Decision-making Tool (provider-patient interaction),
#             7 items, 1-5
#   attitude  Diabetes Self-management Attitude Scale, 10 items, 1-5
#   selfeff   Korean-modified Self-Efficacy for Diabetes Scale, 8 items, 1-10
#   function  Washington Group Short Set on Functioning, 6 items, 1-4
#
# ACCESS3/4/5/7 also have "_R" reverse-coded duplicate columns (verified
# ACCESS_i + ACCESS_i_R == 1 for every row) -- these are the same raw item
# recoded, not new items, so only the non-"_R" (original direction) version
# is kept, per "don't recode reverse-scored items" / avoid duplicate items.
#
# The source "ID" column is corrupted for 30/214 rows (values like
# "175_8", "208_!3" -- non-numeric, apparent data-entry artifacts) and
# pd.to_numeric coercion would silently drop those 30 real respondents.
# Per datastandard.md's "Text IDs that cannot be made numeric" guidance,
# the row index is used as `id` instead so all 214 respondents are kept.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0299971.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Sex": "cov_sex",
    "Age": "cov_age",
    "Education": "cov_education",
    "M_income": "cov_income",
    "disability_degree": "cov_disability_degree",
    "DB_year": "cov_diabetes_years",
    "injection": "cov_insulin_injection",
}

HL_ITEMS = [f"HL{i}" for i in range(1, 65)] + ["Hl65", "HL66"]
SC_ITEMS = [f"SC{i}" for i in range(1, 16)]
ACCESS_ITEMS = [f"ACCESS{i}" for i in range(1, 11)]
INT_ITEMS = [f"INT{i}" for i in range(1, 8)]
ATT_ITEMS = [f"ATT{i}" for i in range(1, 11)]
SE_ITEMS = [f"SE{i}" for i in range(1, 9)]
FL_ITEMS = [f"FL{i}" for i in range(1, 7)]

# (out_name, item_cols, valid_min, valid_max)
SCALES = [
    ("nam_2024_khlat", HL_ITEMS, 1, 4),
    ("nam_2024_selfcare", SC_ITEMS, 1, 4),
    ("nam_2024_access", ACCESS_ITEMS, 0, 1),
    ("nam_2024_medint", INT_ITEMS, 1, 5),
    ("nam_2024_attitude", ATT_ITEMS, 1, 5),
    ("nam_2024_selfeff", SE_ITEMS, 1, 10),
    ("nam_2024_function", FL_ITEMS, 1, 4),
]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Raw_Data")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df), "id not unique"

    cov_present = {k: v for k, v in COV_RENAME.items() if k in df.columns}
    df = df.rename(columns=cov_present)
    cov_cols = list(cov_present.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, item_cols, vmin, vmax in SCALES:
        missing = [c for c in item_cols if c not in df.columns]
        assert not missing, f"{out_name}: missing columns {missing}"

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= vmin) & (long["resp"] <= vmax)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)

        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
