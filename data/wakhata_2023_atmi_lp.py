#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/cb4pmz9rnk
# DOI (data): 10.17632/cb4pmz9rnk
# DOI (paper): 10.1016/j.dib.2023.109055
# Data: Wakhata, R., Mutarutinya, V., & Balimuttajjo, S. (2023). Dataset on the
#   relationship between students' attitude towards, and performance in
#   mathematics word problems, mediated by active learning heuristic
#   problem-solving approach. Data in Brief, 48, 109055. Mendeley Data file
#   "Dataset_Performance and Attitude.xlsx"; instruments in the deposit's
#   "Supplementary material for DIB.zip" (ATMI-SF.pdf, ALHPSA.pdf).
# License: CC BY-NC 3.0, verified on the Mendeley Data record (data_licence).
#   Derived licence carries the NC term. Paper CC BY.
#
# Found by the repos sweep of 2026-11-10 (lane C, Step 2b recoverable_format).
#
# 608 grade-11 students in eight intact classes in Mukono and Mbale, Uganda,
#   2020-21; four classes taught linear programming (LP) with the active
#   learning heuristic problem-solving (ALHPS) approach, four as usual
#   (classes assigned by coin toss). Checked against the paper: N = 608,
#   267 male / 341 female, ages 17-22 -- all reproduce.
#
# ONE output table:
#   wakhata_2023_atmi_lp  A1..A14, the ATMI-SF adapted to LP word problems
#     (14 content items; the 15th, an attention check, is not deposited),
#     1-5 (SD, D, N, A, SA per ATMI-SF.pdf), given after the intervention
#     ("post-attitude", paper section 2). The item mean equals the deposit's
#     Attitu column on every row. The four anxiety items (A5-A8) correlate
#     positively with the rest, so they appear to be stored reverse-scored;
#     the paper does not say, and they are shipped as deposited.
#   treat = Group (paper Table 1: 0 = comparison, 1 = experimental).
# NOT SHIPPED, left as a lead: the ALHPSA questionnaire (G01-G03, PS01-PS04,
#   NEA01-NEA05). On the nine PS/NEA items response 4 is used 0-7 times out of
#   608 while 5 is used 27-64 times, a gap the 1-5 SD-SA anchors cannot
#   explain; the three G items use 4 normally. Held for a look at the coding.
# Dropped: Pre_t / Post_t (LP achievement test percentage totals, no item
#   data), G / PS / NEA / AL / Attitu (subscale means).
# Covariates (paper Table 1): gender (1 = male, 2 = female), age (years),
#   school location (0 = Central, 1 = Western), school status
#   (0 = boarding, 1 = day), school ownership (0 = government, 1 = private).
# `id` is the row index (the deposit has none).
#
# Item text: NOT SHIPPED. ATMI-SF.pdf in the deposit prints all 15 stems, but
#   the instrument is Lim & Chapman's (2013) ATMI-SF (after Tapia & Marsh),
#   adapted, and it has no rights-register row; the deposit's CC BY-NC covers
#   the depositors' material, not the instrument.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("WAKHATA_RAW", "Dataset_Performance and Attitude.xlsx")
ITEMS = [f"A{i}" for i in range(1, 15)]
COVS = {"Gdr": "cov_gender", "Age": "cov_age", "Sch_Location": "cov_school_location",
        "Sch_Status": "cov_school_status", "Sch_Ownership": "cov_school_ownership"}


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (608, 39), d.shape
    assert ((d[ITEMS].mean(axis=1) - d["Attitu"]).abs() < 1e-9).all()
    assert d["Gdr"].value_counts().to_dict() == {2: 341, 1: 267}
    d["id"] = range(1, len(d) + 1)
    d["treat"] = d["Group"].astype(int)
    assert set(d["treat"]) == {0, 1}
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    long = d[["id", "treat"] + covs + ITEMS].melt(id_vars=["id", "treat"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp", "treat"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    name = "wakhata_2023_atmi_lp"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
