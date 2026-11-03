#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0349770
# DOI: 10.1371/journal.pone.0349770
# Paper: Nguyen HTN, Nguyen PH, Nong HTN, et al. (2026). Occupational stress,
#   coping strategies, and associated factors among primary healthcare
#   workers in Vietnam. PLOS ONE.
# Data: S1 Dataset "PSS data" (journal.pone.0349770.s001, .xls), 212
#   primary-healthcare workers in Vietnam (217 rows; the last five hold only
#   stray tallies -- 47, 144, 21, 0 -- in the Education column, and are
#   dropped).
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table:
#   nguyen_2026_phc_pss10  Perceived Stress Scale-10 (Vietnamese version),
#     a1..A10, 0 never .. 4 very often, RAW answers: the four positively
#     worded items (4, 5, 7, 8) are not reversed in the file -- the raw item
#     sum averages 16.3 (paper: 16.7), the reverse-scored sum 18.6.
# NOT shipped: the Brief COPE (B1..b28, 1-4). Its subscale means do not
#   reconcile with the paper in either direction (paper: denial 5.8; items
#   B3+B8 average 3.7 raw and 6.3 reversed; substance use 5.0 vs 3.3 / 6.7),
#   so the item order or coding cannot be established.
# Covariates: age, gender (0 male / 1 female: 130 men is the paper's 61.3%
#   male), years of experience, and 0/1 indicators the paper's Table 1
#   reports as yes/no: alcohol, smoking, chronic disease, psychological
#   disorder, living with others. Dropped, because their codes have no labels
#   in the file: Ethnicity,
#   Religion, Education, the household-member indicators, Relationships, Job
#   title, Heavy workload, Work environment.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Column codes only; the Vietnamese PSS-10 wording is
#   not in the article or SI.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("NGUYEN_PSS_RAW", "journal.pone.0349770.s001.xls")
ITEMS = ["a1", "a2", "a3", "a4", "a5", "A6", "A7", "A8", "A9", "A10"]
BINARY = {"Alcohol": "cov_alcohol", "Smoking": "cov_smoking", "Chronic disease": "cov_chronic_disease",
          "Psychological disorders": "cov_psychological_disorder", "Living with others": "cov_living_with_others"}
DROPPED = {"Ethnicity", "Religion", "Education", "Spouse", "Children", "Biological parents or Parents-in-law",
           "Other relatives", "Relationships", "Job title", "Heavy workload", "Work environment"}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (217, 57), df.shape
    stray = df[df["gender"].isna()]
    assert len(stray) == 5 and stray.drop(columns=["Education"]).isna().all().all()
    df = df[df["gender"].notna()].copy()
    assert len(df) == 212
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert df["gender"].value_counts().to_dict() == {0: 130, 1: 82}
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["age"]
    df["cov_gender"] = df["gender"].map({0: "male", 1: "female"})
    df["cov_years_experience"] = df["Years of experience "]
    for s, t in BINARY.items():
        df[t] = df[s].astype("Int64")
    covs = ["cov_age", "cov_gender", "cov_years_experience"] + list(BINARY.values())
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert set(long["resp"]) <= {0, 1, 2, 3, 4}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3, 4] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    cope = {c for c in df.columns if c.lower().startswith("b") and c[1:].isdigit()}
    assert len(cope) == 28
    used = set(ITEMS) | cope | DROPPED | set(BINARY) | {"age", "gender", "Years of experience "}
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "nguyen_2026_phc_pss10.csv"), index=False)
    print(f"nguyen_2026_phc_pss10: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
