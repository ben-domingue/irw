#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/CEOWED
# DOI (data): 10.7910/DVN/CEOWED
# DOI (paper): 10.3352/jeehp.2023.20.16
# Data: Ezeala, M. I. O., & Volk, J. (2023). Relationships between
#   undergraduate medical students' attitudes toward communication skills
#   learning and demographics in Zambia: a survey-based descriptive study.
#   Journal of Educational Evaluation for Health Professions, 20, 16.
#   Harvard Dataverse "jeehp-20-16-dataset1.xlsx" (Sheet1 = data; Sheet2 =
#   the 26 CSAS statements with their positive/negative subscale and the
#   5 = strongly agree ... 1 = strongly disagree key).
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper: 369 participants; mean CSAS total 103.6 -- the
#   deposit's Total and the item sum both give 103.6 (they agree on 367 of
#   369 rows).
#
# ONE output table:
#   ezeala_2023_csas  V1..V26, the Communication Skills Attitude Scale (Rees,
#     Sheard & Davies 2002), 1 = strongly disagree ... 5 = strongly agree.
#     Because the item sum equals the reported total (which the CSAS scores
#     with negative items reversed), the 13 negative items are stored
#     already reversed; they ship as stored.
# Covariates: academic year (Level), age, sex (1/2, unlabeled), school, mode
#   (unlabeled codes as deposited).
# `id` is the row index.
#
# Item text: NOT SHIPPED. Sheet2 holds the 26 English statements, but CSAS
#   (Rees et al. 2002) has no register row.

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

RAW = os.environ.get("EZEALA_RAW", "jeehp-20-16-dataset1.xlsx")
COVS = {"Level": "cov_year", "Age": "cov_age", "Sex": "cov_sex", "School": "cov_school", "Mode": "cov_mode"}


def convert():
    d = pd.read_excel(RAW, sheet_name="Sheet1")
    assert d.shape == (369, 32)
    items = [f"V{k}" for k in range(1, 27)]
    tot = d[items].sum(axis=1)
    assert round(tot.mean(), 1) == 103.6 and (tot == d["Total"]).sum() == 367
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns=COVS)
    write(d, items, [1, 2, 3, 4, 5], "ezeala_2023_csas", list(COVS.values()))


if __name__ == "__main__":
    convert()
