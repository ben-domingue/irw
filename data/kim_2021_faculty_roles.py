#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/EVYTJP
# DOI (data): 10.7910/DVN/EVYTJP
# DOI (paper): 10.3352/jeehp.2021.18.28
# Data: Kim, Cho, & Chung (2021). Newly appointed medical faculty members'
#   self-evaluation of their educational roles at the Catholic University of
#   Korea College of Medicine in 2020 and 2021: a cross-sectional survey-based
#   study. Journal of Educational Evaluation for Health Professions, 18, 28.
#   Harvard Dataverse "Dataset 1. Raw response data from 100 participating new
#   faculty members ..." (sheet "raw data").
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# 100 newly appointed faculty rated 12 educational roles (Harden & Crosby's
# 12 roles of the medical teacher: lecturer, clinical teacher, on-the-job role
# model, teaching role model, mentor, learning facilitator, assessment
# planner, curriculum evaluator, curriculum planner, course organiser, study
# guide producer, learning-resource developer) on three questions, each 1-5.
# THREE output tables, one per question (same 12 roles):
#   kim_2021_faculty_roles_importance  importance to the medical school
#   kim_2021_faculty_roles_current     current personal commitment
#   kim_2021_faculty_roles_preferred   preferred personal future commitment
#   item = role01..role12 in the deposit's column order (column triplets).
#   Checked: 100 respondents (header rows 0-4 are category / number / role /
#   question labels), no missing cells, all values 1-5.
# No covariates in the file. `id` is the deposit's No.
#
# Item text: not shipped -- role descriptions are in the header, but there is
#   no register row.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KIMFAC_RAW", "Dataset 1. Raw response data from 100 participating new faculty members.xlsx")
QUESTIONS = [("Importance", "importance"), ("Current", "current"), ("Preferred", "preferred")]


def convert():
    raw = pd.read_excel(RAW, sheet_name="raw data", header=None)
    labels = [str(x).strip() for x in raw.iloc[4, 1:37]]
    d = raw.iloc[5:].reset_index(drop=True)
    assert len(d) == 100 and d[0].is_unique
    for k, (label, short) in enumerate(QUESTIONS):
        cols = list(range(1 + k, 37, 3))
        assert all(labels[c - 1].startswith(label) for c in cols), [labels[c - 1] for c in cols]
        sub = d[cols].apply(pd.to_numeric, errors="raise")
        sub.columns = [f"role{i:02d}" for i in range(1, 13)]
        sub.insert(0, "id", d[0].astype(int))
        long = sub.melt(id_vars="id", var_name="item", value_name="resp").dropna(subset=["resp"])
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        long["resp"] = long["resp"].astype(int)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in long["item"].unique()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        name = f"kim_2021_faculty_roles_{short}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
