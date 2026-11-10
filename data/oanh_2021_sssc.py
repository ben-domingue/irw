#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/16AUXV
# DOI (data): 10.7910/DVN/16AUXV
# DOI (paper): 10.3352/jeehp.2021.18.16
# Data: Oanh, T. T. H., Hoai, N. T. Y., & Thuy, P. T. (2021). The
#   relationships of nursing students' satisfaction and self-confidence after
#   a simulation-based course with their self-confidence while practicing on
#   real patients in Vietnam. Journal of Educational Evaluation for Health
#   Professions, 18, 16. Harvard Dataverse: dataset1 (sheet "SIMULATION
#   SELF-CONFIDENCE AND ...", the NLN Student Satisfaction and Self-Confidence
#   in Learning items) and the C-scale responses file.
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper: 182 second-year nursing students, 98.4% female
#   (179, Gender = 1) -- reproduces.
#
# TWO output tables (same 182 students, same row order and Gender/Age/GPA in
#   both files -- asserted -- so the ids link):
#   oanh_2021_sssc  III.a.1-5 satisfaction and III.b.6-13 self-confidence,
#     the NLN SSSCL, 1 = strongly disagree ... 5 = strongly agree. Two cells
#     hold 6, which a 5-point scale cannot take (isolated, data entry
#     errors), and are dropped.
#   oanh_2021_confidence_scale  C1..C5, the Confidence Scale (self-confidence
#     while practicing on real patients), 1-5 as deposited.
# Covariates: gender (1 = female, 2 = male per the paper's 98.4%), age, GPA.
#   The subscale means (IIIA, IIIB, C) are composites and dropped.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Codes only; NLN SSSCL has no register row.

import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")


def write(d, items, permitted, name, covs, codes=None, drop_values=()):
    codes = codes or items
    sub = d[["id"] + covs + items].rename(columns=dict(zip(items, codes)))
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[~long["resp"].isin(drop_values)]
    assert (long["resp"] == np.floor(long["resp"])).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted), set(long["resp"])
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

RAW1 = os.environ.get("OANH_RAW1", "sssc.xlsx")
RAW2 = os.environ.get("OANH_RAW2", "cscale.xlsx")


def convert():
    a = pd.read_excel(RAW1)
    b = pd.read_excel(RAW2)
    assert a.shape == (182, 18) and b.shape == (182, 9)
    assert (a[["Gender", "Age", "GPA"]].fillna(-1).values == b[["Gender", "Age", "GPA"]].fillna(-1).values).all()
    assert (a["Gender"] == 1).sum() == 179
    for d in (a, b):
        d["id"] = range(1, len(d) + 1)
        d["cov_gender"] = d["Gender"].map({1: "female", 2: "male"})
        d["cov_age"] = d["Age"]
        d["cov_gpa"] = d["GPA"]
    covs = ["cov_gender", "cov_age", "cov_gpa"]
    sitems = list(a.columns[3:16])
    assert sitems[0] == "III.a.1" and sitems[-1] == "III.b.13"
    assert (a[sitems] == 6).sum().sum() == 2
    write(a, sitems, [1, 2, 3, 4, 5], "oanh_2021_sssc", covs, drop_values=(6,))
    write(b, [f"C{k}" for k in range(1, 6)], [1, 2, 3, 4, 5], "oanh_2021_confidence_scale", covs)


if __name__ == "__main__":
    convert()
