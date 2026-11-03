#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0220944
# DOI: 10.1371/journal.pone.0220944
# Paper: Lin MH, Chang TH, Lee YH, Wang PY, Lin LH, Hsu HC (2019). Developing
#   and validating the Nursing Cultural Competence Scale in Taiwan. PLOS ONE
#   14(8): e0220944.
# Data: S5 File "NCCS-minimal underlying data set" (journal.pone.0220944.s005,
#   .xlsx), 246 clinical nurses in Taiwan.
# Scale: S3 File (English), S4 File (the Chinese NMCCS it was validated
#   against).
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table:
#   lin_2019_nccs  Nursing Cultural Competence Scale, 19 items C1..C19
#     (cultural knowledge C1-7, cultural skills C8-13, cultural seeking
#     C14-19, per S3 File's three stems). The paper describes the response
#     scale as 1 "rarely", 2 "occasionally", 3 "neutrally", 4 "often", 5
#     "always"; the deposit codes the same five points 0-4, ascending, and is
#     shipped as deposited (resp 0 = rarely .. 4 = always).
# Covariates: age, years working as a nurse (years + months/12). Dropped,
#   because their codes have no labels in the file or the paper: Marital
#   Status, Education, Clinical Ladder System, Department, caring for
#   foreigners.
# `id` is the deposit's own ID column.
#
# Item text: NOT SHIPPED. English item stems are in S3 File
#   (journal.pone.0220944.s003), but the scale was developed and
#   administered in Chinese and the Chinese NCCS wording is not in the
#   deposit (S4 File is a different instrument, the NMCCS).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LIN_NCCS_RAW", "journal.pone.0220944.s005.xlsx")
ITEMS = [f"C{i}" for i in range(1, 20)]
DROPPED = {"Marital Status", "Education", "Clinical Ladder System", "Department", "caring for foreigners"}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (246, 28), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert df["ID"].is_unique
    df["id"] = df["ID"]
    df["cov_age"] = df["age"]
    df["cov_years_nursing"] = (df["working as nurses (year)"] + df["working as nurses (month)"] / 12).round(2)
    covs = ["cov_age", "cov_years_nursing"]
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
    used = set(ITEMS) | DROPPED | {"ID", "age", "working as nurses (year)", "working as nurses (month)"}
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "lin_2019_nccs.csv"), index=False)
    print(f"lin_2019_nccs: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
