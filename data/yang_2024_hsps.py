#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0309904
# DOI: 10.1371/journal.pone.0309904
# Paper: Yang, W., & Kwon, M. (2024). Cut-off scores for sensitivity
#   interpretation of the Korean Highly Sensitive Person Scale. PLOS ONE
#   19(9): e0309904.
# Data: Zenodo 10.5281/zenodo.13193336, "HSPS_KOREAN_cut-off-scores",
#   file HSPS_Korean_Cut-off-scores_1773.csv: 1,773 Korean adults.
# License: CC BY 4.0, verified ON THE DEPOSIT (Zenodo record metadata
#   license id cc-by-4.0); the article is also CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, yang_2024_hsps: s1..s27, the 27-item Highly Sensitive
# Person Scale (Aron & Aron 1997), Korean version, 1-7. Shipped as deposited.
# s3 is read as text because one cell holds a blank (" "); it is a missing
# response and is dropped. HSPSf1..f3 and HSPSsum are derived subscale and
# total scores, not shipped.
#
# Covariates: gender (F/M as deposited) and age, which the deposit records
# only as a decade band (20, 30, .. 80) -- shipped as cov_age_decade.
#
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. The deposit is one CSV with s1..s27 headers and no
#   codebook; the Korean wording is not in the article. The HSPS is a named
#   third-party instrument.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("YANG_RAW", "HSPS_Korean_Cut-off-scores_1773.csv")
NAME = "yang_2024_hsps"
N_ROWS = 1773


def convert():
    df = pd.read_csv(RAW, encoding="utf-8-sig")
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 33 and txt == ["s3", "Gender"]
    assert set(df["Gender"]) == {"F", "M"}
    assert set(df["s3"].str.strip()) <= {"", *map(str, range(1, 8))}
    items = [f"s{i}" for i in range(1, 28)]
    df["s3"] = pd.to_numeric(df["s3"].str.strip().replace("", None))
    print(f"s3 blanks dropped: {int(df['s3'].isna().sum())}")

    df["id"] = range(1, N_ROWS + 1)
    df["cov_gender"] = df["Gender"]
    df["cov_age_decade"] = df["Age"]
    cov_cols = ["cov_gender", "cov_age_decade"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item",
                                              value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == set(range(1, 8))
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any() and long["item"].nunique() == 27
    checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    accounted = set(items) | {"HSPSf1", "HSPSf2", "HSPSf3", "HSPSsum", "Gender", "Age", "id",
                              "cov_gender", "cov_age_decade"}
    assert set(df.columns) == accounted
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; "
          "dropped HSPSf1-3, HSPSsum (derived)")


if __name__ == "__main__":
    convert()
