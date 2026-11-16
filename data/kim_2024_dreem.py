#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ZINJH6
# DOI (data): 10.7910/DVN/ZINJH6
# DOI (paper): 10.3352/jeehp.2024.21.20
# Data: Kim, M.-K., & Kim, H. W. (2024). Impact of a change from A-F grading to
#   honors/pass/fail grading on academic performance at Yonsei University
#   College of Medicine in Korea: a cross-sectional serial mediation analysis.
#   Journal of Educational Evaluation for Health Professions, 21, 20.
#   Harvard Dataverse "jeehp-21-20-dataset1.xlsx", sheet HPF_rawdata_JEEHP.
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# TWO output tables (238 second-year medical students, 2014 n=127 A-F
# grading, 2015 n=111 honors/pass/fail; both counts reproduce):
#   kim_2024_dreem    DREEM1..DREEM50, Dundee Ready Education Environment
#     Measure, 0-4 (deposit "Variables, Scales" sheet). Raw (unreversed)
#     responses from the rawdata sheet; items 4, 8, 9, 17, 25, 35, 39, 48 and
#     50 are negatively worded (reversed in the deposit's coding sheet, where
#     raw + reversed = 4 on every row, confirming the rawdata sheet is raw).
#     Out-of-range cells (values 5, 6, 33 -- isolated data-entry errors) are
#     dropped; the count is printed.
#   kim_2024_ams_im   IM1..IM12, the intrinsic-motivation items of the
#     Academic Motivation Scale (IM1=AMS2, IM2=AMS4, IM3=AMS6, IM4=AMS9,
#     IM5=AMS11, IM6=AMS13, IM7=AMS16, IM8=AMS18, IM9=AMS20, IM10=AMS23,
#     IM11=AMS25, IM12=AMS27), 1-7. Item sums reproduce total.IM.
# Covariates: grading system, sex, admission type (labels from the deposit's
#   Variables sheet), Basic Medical Science Examination score (0-100).
# `id` is the deposit's ID (a row counter 1..238).
#
# Item text: not shipped -- codes only in the deposit; DREEM and AMS have no
#   register row.

import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KIM_RAW", "jeehp-21-20-dataset1.xlsx")
COVS = ["cov_grading_system", "cov_sex", "cov_admission_type", "cov_bmse_score"]


def write(d, items, permitted, name):
    long = d[["id"] + COVS + items].melt(id_vars=["id"] + COVS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    bad = ~long["resp"].isin(permitted)
    print(f"{name}: dropping {bad.sum()} out-of-range cells")
    long = long[~bad]
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + COVS]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    d = pd.read_excel(RAW, sheet_name="HPF_rawdata_JEEHP")
    assert d.shape == (238, 67) and d["ID"].is_unique
    d["id"] = d["ID"]
    d["cov_grading_system"] = d["grading.system"].map({0: "A-F", 1: "honors/pass/fail"})
    d["cov_sex"] = d["sex"].map({0: "male", 1: "female"})
    d["cov_admission_type"] = d["admission.type"].map({0: "undergraduate-entry", 1: "graduate-entry"})
    d["cov_bmse_score"] = d["performance"]
    assert d[COVS].notna().all().all()
    write(d, [f"DREEM{i}" for i in range(1, 51)], [0, 1, 2, 3, 4], "kim_2024_dreem")
    im = [f"IM{i}" for i in range(1, 13)]
    write(d, im, [1, 2, 3, 4, 5, 6, 7], "kim_2024_ams_im")


if __name__ == "__main__":
    convert()
