#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/Y1VZUK
# DOI (data): 10.7910/DVN/Y1VZUK
# DOI (paper): 10.3352/jeehp.2023.20.26
# Data: Huang, P.-H., O'Sullivan, A. J., & Shulruf, B. (2023). Development and
#   validation of the student ratings in clinical teaching scale in
#   Australia: a methodological study. Journal of Educational Evaluation for
#   Health Professions, 20, 26. Harvard Dataverse "jeehp-20-26-dataset1.xlsx",
#   sheets "data" and "variable_view" (the file guide).
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper: 352 UNSW medical students (years 2, 3, 6, 2018),
#   157 men and 183 women (Gender 1/2) -- reproduces.
#
# ONE output table:
#   huang_2023_strict  Q1..Q78, the 78 draft STRICT items (students' ratings
#     of how often their clinical teachers showed each behaviour),
#     1 = never, 2 = rarely, 3 = occasionally, 4 = often, 5 = very often,
#     6 = always (file guide). The paper's EFA kept a subset; all 78 ship.
#   MEAN-IMPUTED CELLS DROPPED: 155 cells hold non-integer values (e.g.
#     3.6959...); every one equals its column's mean over the integer cells
#     (checked), so they are mean imputations, not responses (datastandard: a
#     fractional value on an integer scale is an imputation until proven
#     otherwise). The integer cells ship as recorded.
# Covariates (file guide): gender (1 male, 2 female, 3 prefer not to answer),
#   age (years), year of study, English as first language, domestic or
#   international student.
# `id` is the deposit's Number.
#
# Item text: NOT SHIPPED. The 78 items are in the paper's Supplement 1, not
#   in the deposit.

import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("HUANG_RAW", "jeehp-20-26-dataset1.xlsx")
ITEMS = [f"Q{k}" for k in range(1, 79)]


def convert():
    d = pd.read_excel(RAW, sheet_name="data")
    assert d.shape == (352, 84)
    assert d["Number"].is_unique
    assert (d["Gender"] == 1).sum() == 157 and (d["Gender"] == 2).sum() == 183
    d["id"] = d["Number"].astype(int)
    d["cov_gender"] = d["Gender"].map({1: "male", 2: "female", 3: "prefer not to answer"})
    d["cov_age"] = d["Age"]
    d["cov_year"] = d["Year"]
    d["cov_english_first_language"] = d["NativeEng"].map({1: "yes", 2: "no"})
    d["cov_student_status"] = d["Status"].map({1: "domestic", 2: "international"})
    covs = ["cov_gender", "cov_age", "cov_year", "cov_english_first_language", "cov_student_status"]
    long = d[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    frac = long["resp"] != np.floor(long["resp"])
    print(f"  dropping {frac.sum()} mean-imputed (non-integer) cells")
    assert frac.sum() == 155, frac.sum()
    long = long[~frac].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5, 6}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5, 6] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    name = "huang_2023_strict"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
