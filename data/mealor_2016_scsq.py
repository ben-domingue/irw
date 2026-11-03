#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0155483
# DOI: 10.1371/journal.pone.0155483
# Paper: Mealor, A. D., Simner, J., Rothen, N., Carmichael, D. A., & Ward, J.
#   (2016). Different dimensions of cognitive style in typical and atypical
#   cognition: New evidence and a new measurement tool. PLOS ONE 11(5):
#   e0155483.
# Data: journal.pone.0155483.s001 (S1 File, "Study 1 Data -- Item scores on
#   each SCSQ item", .xlsx): 1,455 UK adults (University of Sussex and
#   community), after the paper's exclusion of 87 self-reported possible
#   synaesthetes. S1 Table (.docx) lists all 84 items in their item-number
#   order with the source instrument of each.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, mealor_2016_scsq: ITEM00001..ITEM00084, the 84-item pool
# of the Sussex Cognitive Styles Questionnaire as administered (Study 1), all
# on one five-point scale, 1 strongly disagree .. 5 strongly agree (Methods:
# "All items were measured on a five point Likert scale ... from 'strongly
# disagree' to 'strongly agree'"). One administration, one response format,
# so one table even though the pool draws on several sources. Shipped as
# deposited; no item is reversed. S2/S3 Files are factor scores (aggregates)
# and are not shipped.
#
# Covariates: gender (0 = female: 907, exactly the paper's "907 females,
# 548 males") and birth year (the questionnaire asked birth year only).
#
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. All 84 stems are in S1 Table, keyed by the same
#   item numbers, so the mapping is cheap. The rights are not: 57 of the 84
#   items are reproduced from third-party instruments (OSIVQ 22, Systemizing
#   Quotient 24, Autism-Spectrum Quotient 7, IDQ 4), only 27 are new. A
#   partial table of the 27 new items (study-authored, CC BY) is possible on
#   a later pass.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("MEALOR_RAW", "journal.pone.0155483.s001.xlsx")
NAME = "mealor_2016_scsq"
N_ROWS = 1455


def convert():
    df = pd.read_excel(RAW).copy()
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 86 and txt == []
    items = [f"ITEM{i:05d}" for i in range(1, 85)]
    assert list(df.columns) == ["gender", "birthYear"] + items
    assert df["gender"].value_counts().to_dict() == {0: 907, 1: 548}

    df["id"] = range(1, N_ROWS + 1)
    df["cov_gender"] = df["gender"].map({0: "female", 1: "male"})
    df["cov_birth_year"] = df["birthYear"]
    cov_cols = ["cov_gender", "cov_birth_year"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item",
                                              value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
