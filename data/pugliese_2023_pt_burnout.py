#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XAPD4U
# DOI (data): 10.7910/DVN/XAPD4U
# DOI (paper): 10.3352/jeehp.2023.20.27
# Data: Pugliese, M., Brismee, J.-M., Allen, B., Riley, S., Tammany, J., &
#   Mintken, P. (2023). Mentorship and self-efficacy are associated with lower
#   burnout in physical therapists in the United States: a cross-sectional
#   survey study. Journal of Educational Evaluation for Health Professions,
#   20, 27. Harvard Dataverse "jeehp-20-27-dataset2.xlsx" (sheet "Coded
#   Data-JEEHP-8.31.23"; full question wording as headers). dataset1.csv is
#   the raw SurveyMonkey export of the same survey and is not used (its IP,
#   email and name columns are present but empty).
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper's abstract: 2,813 physical therapists, 68.72%
#   female (1,933), 80.13% White (2,254), 77.14% full-time (2,170) -- all
#   reproduce. One further row (2,814th) is empty and dropped.
#
# TWO output tables (item codes are positional in the file's column order;
#   the header text of each column is in BCSQ / GSE below):
#   pugliese_2023_bcsq12  Burnout Clinical Subtypes Questionnaire (BCSQ-12,
#     Montero-Marin et al.), 12 items, 1-7 as deposited (the paper sums them:
#     median BCSQ-12 = 42). bcsq_01..bcsq_12.
#   pugliese_2023_gses  General Self-Efficacy Scale (Schwarzer & Jerusalem),
#     10 items, 1-4 as deposited. gses_01..gses_10 in the canonical GSE item
#     order (the headers are the ten GSE stems, verbatim, in order).
# Dropped: the subscale and total scores, the self-reported burnout yes/no
#   (kept as a covariate), job-role and mentorship checklists.
# Covariates: age, gender, race/ethnicity, state of practice, years of
#   clinical experience, practice setting, care delivery model, highest PT
#   degree, weekly patient-care hours, self-reported burnout (0/1).
# `id` is the row index.
#
# Item text: NOT SHIPPED in this batch. GSE is a register `ship` (FU Berlin
#   FAQ grant) and its stems are this file's column headers (data_labels), so
#   pugliese_2023_gses is a cheap follow-up once the 1-4 anchors are sourced
#   (the deposit codes them without labels). BCSQ-12 has no register row.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("PUGLIESE_RAW", "jeehp-20-27-dataset2.xlsx")
COVS = {1: "cov_age", 2: "cov_gender", 3: "cov_race", 4: "cov_state", 6: "cov_years_experience",
        9: "cov_setting", 10: "cov_delivery_model", 11: "cov_degree", 8: "cov_patient_care_hours",
        62: "cov_self_reported_burnout"}


def write(d, cols, prefix, permitted, name, covs):
    codes = [f"{prefix}_{k:02d}" for k in range(1, len(cols) + 1)]
    sub = d[["id"] + covs + cols].rename(columns=dict(zip(cols, codes)))
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted), set(long["resp"])
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")
    return dict(zip(codes, cols))


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (2814, 68), d.shape
    bcsq, gse = list(d.columns[40:52]), list(d.columns[52:62])
    assert d.columns[66] == "Total BCSQ-12" and d.columns[67] == "Total GSES"
    assert gse[0].startswith("I can always manage to solve difficult problems")
    d = d[d[bcsq + gse].notna().all(axis=1)].copy()
    assert len(d) == 2813
    assert (d[bcsq].sum(axis=1) == d["Total BCSQ-12"]).all()
    assert (d[gse].sum(axis=1) == d["Total GSES"]).all()
    assert (d.iloc[:, 2] == "Female").sum() == 1933
    d["id"] = range(1, len(d) + 1)
    for i, name in COVS.items():
        d[name] = d.iloc[:, i]
    covs = list(COVS.values())
    os.makedirs(OUT_DIR, exist_ok=True)
    global BCSQ, GSE
    BCSQ = write(d, bcsq, "bcsq", list(range(1, 8)), "pugliese_2023_bcsq12", covs)
    GSE = write(d, gse, "gses", [1, 2, 3, 4], "pugliese_2023_gses", covs)


BCSQ, GSE = {}, {}

if __name__ == "__main__":
    convert()
