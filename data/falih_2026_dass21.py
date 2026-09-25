#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/8YLSMK
# DOI: 10.7910/DVN/8YLSMK
# License: CC0 1.0
#
# DASS-21 (21 items, 0-3 scale), all three subscales (depression, anxiety,
# stress) administered together as one instrument -- kept as one file per
# datastandard.md, not split by subscale.
# Raw file also contains the Maladaptive Daydreaming Scale-16 (separate
# instrument, different response scale) -- shipped as its own file,
# falih_2026_mds16.py, per datastandard.md's "one instrument per file" rule.
#
# Six columns in the raw file (MDS16, DASS21, DEPRESSI, ANXIETY, STRESS,
# V52) are all-null section-header artifacts from the source spreadsheet,
# not data -- dropped rather than shipped as empty items/covariates.
#
# The same author deposited the same 262 respondents' DASS-21 again as
# doi:10.7910/DVN/TAISB2 (data.xlsx), which IRW had published separately as
# dass21_depression_anxiety_stress (withdrawn 2026-09-25, irw#2424). Checked:
# same ids ("No."), sex/marital/smoking equal for all 262, TAISB2 "Age" equals
# AGEGROUP, and 5,500/5,502 DASS cells equal -- the 2 that differ are
# out-of-range 4s in TAISB2 (ids 69 q1, 218 q6), so responses come from this
# deposit. TAISB2 adds four covariates this file lacks; they are merged by id:
# cov_education, cov_monthly_income, cov_weekly_working_hours, cov_caffeine
# (numeric codes, as deposited; no codebook in either deposit).

from __future__ import annotations

from pathlib import Path

import sys

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from irw_validate.compat import run_qc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

FILE_URL = "https://dataverse.harvard.edu/api/access/datafile/13638063"
TAISB2_URL = "https://dataverse.harvard.edu/api/access/datafile/13891169"   # data.xlsx, doi:10.7910/DVN/TAISB2
TAISB2_COVS = {"Education": "cov_education", "Monthly income": "cov_monthly_income",
               "Weekly working hours": "cov_weekly_working_hours", "Caffeine": "cov_caffeine"}
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DASS_ITEMS = [
    "Q1_A", "Q2_A", "Q3_A", "Q4_A", "Q5_A", "Q6_A", "Q7_A", "Q8_A", "Q9_A",
    "Q10_A", "Q11_A", "Q12_A", "Q13_A", "Q14_A", "Q15_A", "Q16_A",
    "Q17", "Q18", "Q19", "Q20", "Q21",
]
COV_MAP = {
    "NO": "id", "AGE": "cov_age", "AGEGROUP": "cov_agegroup",
    "SEX": "cov_sex", "MARITALS": "cov_marital_status",
    "EXPERIEN": "cov_experien", "V7_A": "cov_v7_a",
    "SMOKING": "cov_smoking", "ALCOHOL": "cov_alcohol",
}
COV_COLS = [v for k, v in COV_MAP.items() if v != "id"] + list(TAISB2_COVS.values())


def convert():
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.BytesIO(r.content), sep="\t")
    df = df.rename(columns=COV_MAP)

    assert df["id"].nunique() == len(df), "id not unique"

    t = requests.get(TAISB2_URL, headers=UA, timeout=60)
    t.raise_for_status()
    extra = pd.read_excel(pd.io.common.BytesIO(t.content))
    extra.columns = [c.strip() for c in extra.columns]
    # identity checks before merging: same people, same shared covariates
    j = df.merge(extra, left_on="id", right_on="No.", how="outer", indicator=True)
    assert (j["_merge"] == "both").all(), "TAISB2 and 8YLSMK ids differ"
    for a, b in (("Sex", "cov_sex"), ("Marital status", "cov_marital_status"),
                 ("Smoking", "cov_smoking"), ("Age", "cov_agegroup")):
        assert (j[a] == j[b]).all(), f"TAISB2 {a} disagrees with {b}"
    df = df.merge(extra[["No."] + list(TAISB2_COVS)].rename(columns={"No.": "id", **TAISB2_COVS}),
                  on="id", how="left")

    long = df.melt(id_vars=["id"] + COV_COLS, value_vars=DASS_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 3)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + COV_COLS]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "falih_2026_dass21.csv"
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]
    long.to_csv(out_path, index=False)
    print(f"falih_2026_dass21: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
