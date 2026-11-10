#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XN49KQ
# DOI (data): 10.7910/DVN/XN49KQ
# DOI (paper): 10.3352/jeehp.2024.21.24
# Data: Oanh, T. T. H., Thuy, L. T., & Huyen, N. T. T. (2024). The effect of
#   simulation-based training on problem-solving skills, critical thinking
#   skills, and self-efficacy among nursing students in Vietnam: a
#   before-and-after study. Journal of Educational Evaluation for Health
#   Professions, 21, 24. Harvard Dataverse workbook with sheets "PRE-DATA
#   SIMULATION", "POST - DATA SIMULATION", "PRE&POST" and "CODING".
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper (Supplement 3): 173 students pre and post;
#   item sums reproduce the deposit's own totals on all 173 and the paper's
#   means (problem solving 131.42 / 127.24, critical thinking 119.86 /
#   120.12). The pre sheet's two extra rows are blank (no ID) and dropped.
#
# THREE output tables, each with wave = 1 (pre) / 2 (post), ids = the
#   deposit's ID (the same student in both waves):
#   oanh_2024_ctsq  B1..B34, critical thinking (CTSQ), 1 = never, 2 = rarely,
#     3 = sometimes, 4 = usually, 5 = always (CODING sheet).
#   oanh_2024_psi   C1..C32, Problem Solving Inventory (Heppner), 1 = strongly
#     disagree ... 6 = strongly agree (CODING). The item sum equals the
#     paper's PSI total, so reverse-keyed items are stored as scored.
#   oanh_2024_gses  D1..D10, General Self-Efficacy Scale, 1 = completely
#     incorrect, 2 = almost incorrect, 3 = somewhat correct, 4 = completely
#     correct (CODING).
#   Out-of-range cells (B: one 0 and one 6; C: one 0 and one 45; D: five 5s
#     and one 6, all in single cells) are data-entry errors and dropped.
# Covariates (pre sheet): age, gender (code as deposited; one 13 is an entry
#   error and left empty), residence.
#
# Item text: NOT SHIPPED. Codes only. GSE (register ship) could follow once
#   the Vietnamese wording question is settled; CTSQ and PSI have no rows.

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
    sub = d[["id", "wave"] + covs + items].rename(columns=dict(zip(items, codes)))
    long = sub.melt(id_vars=["id", "wave"] + covs, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    bad = ~long["resp"].isin(permitted)
    print(f"  {name}: dropping {bad.sum()} out-of-range cells {sorted(long.loc[bad, 'resp'].unique())}")
    assert bad.sum() <= 6
    long = long[~bad]
    assert (long["resp"] == np.floor(long["resp"])).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted), set(long["resp"])
    long = long[["id", "item", "resp", "wave"] + covs]
    assert not long.duplicated(["id", "item", "wave"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

RAW = os.environ.get("OANH24_RAW", "dataset.xlsx")


def convert():
    x = pd.read_excel(RAW, sheet_name=None)
    pre = x["PRE-DATA SIMULATION"]
    post = x["POST - DATA SIMULATION"]
    pre = pre[pre["ID"].notna()].copy()
    assert len(pre) == 173 and len(post) == 173 and set(pre["ID"]) == set(post["ID"])
    B = [f"B{k}" for k in range(1, 35)]
    C = [f"C{k}" for k in range(1, 33)]
    D = [f"D{k}" for k in range(1, 11)]
    assert (pre[C].sum(axis=1) == pre["prePSV"]).all() and (post[C].sum(axis=1) == post["postPSV"]).all()
    covs = pre[["ID", "Age", "Gender", "Residence"]].copy()
    covs["Gender"] = covs["Gender"].where(covs["Gender"].isin([0, 1]))
    covs = covs.rename(columns={"Age": "cov_age", "Gender": "cov_gender", "Residence": "cov_residence"})
    pre["wave"] = 1
    post["wave"] = 2
    d = pd.concat([pre[["ID", "wave"] + B + C + D], post[["ID", "wave"] + B + C + D]], ignore_index=True)
    d = d.merge(covs, on="ID", how="left", validate="many_to_one")
    d["id"] = d["ID"].astype(int)
    cv = ["cov_age", "cov_gender", "cov_residence"]
    write(d, B, [1, 2, 3, 4, 5], "oanh_2024_ctsq", cv)
    write(d, C, [1, 2, 3, 4, 5, 6], "oanh_2024_psi", cv)
    write(d, D, [1, 2, 3, 4], "oanh_2024_gses", cv)


if __name__ == "__main__":
    convert()
