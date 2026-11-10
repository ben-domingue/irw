#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/GVZJSH
# DOI (data): 10.7910/DVN/GVZJSH
# DOI (paper): 10.3352/jeehp.2022.19.28
# Data: Naciri, A., Radid, M., Achbani, A., Baba, M. A., Kharbach, A., &
#   Chemsi, G. (2022). Factors affecting nursing and health technician
#   students' satisfaction with distance learning during the COVID-19
#   pandemic in Morocco: a descriptive study. Journal of Educational
#   Evaluation for Health Professions, 19, 28. Harvard Dataverse
#   "jeehp-19-28-dataset1.xlsx", sheet "Data base-excel": 330 data rows,
#   then an in-sheet coding legend (rows 332 on), which this script reads
#   for the labels and does not treat as data.
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper: 330 students, 249 female (75.5%), mean age 20.2,
#   189 generalist nurses -- all reproduce.
#
# ONE output table:
#   naciri_2022_dl_satisfaction  Question1..Question24, the distance-learning
#     satisfaction questionnaire (instructor, technology, course setup,
#     interaction, outcomes, overall), 1 = strongly disagree ... 5 = strongly
#     agree (paper and legend).
# Covariates (labels from the legend): age, gender, nationality, discipline,
#   study level, platform used, internet quality. Score columns are
#   composites and dropped.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Codes only in the deposit.

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

RAW = os.environ.get("NACIRI_RAW", "jeehp-19-28-dataset1.xlsx")
LAB = {"gender": {0: "female", 1: "male"}, "nationality": {0: "Moroccan", 1: "other"},
       "discipline": {0: "Polyvalent nurse", 1: "Midwife", 2: "Nurse in anesthesia and intensive care",
                      3: "Emergency and critical care nurse", 4: "Radiology technician", 5: "Laboratory technician"},
       "study_level": {0: "1st year", 1: "2nd year", 2: "3rd year"},
       "Plateforme": {0: "Whatsapp", 1: "Zoom", 2: "Moodle", 3: "Google Meet", 4: "Edmodo", 5: "Google Classroom",
                      6: "several platforms"},
       "internet_quality": {0: "excellent", 1: "good", 2: "poor"}}


def convert():
    d = pd.read_excel(RAW, sheet_name="Data base-excel")
    items = [f"Question{k}" for k in range(1, 25)]
    d = d.iloc[:330].copy()
    assert d[items].apply(pd.to_numeric, errors="coerce").notna().all().all()
    assert (pd.to_numeric(d["gender"]) == 0).sum() == 249
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = pd.to_numeric(d["Age"], errors="coerce")
    covs = ["cov_age"]
    for src, lab in LAB.items():
        v = pd.to_numeric(d[src], errors="coerce")
        assert set(v.dropna()) <= set(lab), src
        name = {"Plateforme": "cov_platform"}.get(src, "cov_" + src)
        d[name] = v.map(lab)
        covs.append(name)
    write(d, items, [1, 2, 3, 4, 5], "naciri_2022_dl_satisfaction", covs)


if __name__ == "__main__":
    convert()
