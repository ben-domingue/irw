#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/GL0RPU
# DOI (data): 10.7910/DVN/GL0RPU
# DOI (paper): 10.3352/jeehp.2019.16.35
# Data: Dennis, D., Craft, M., Bratzler, D., et al. (2019). Evaluation of
#   student perceptions with 2 interprofessional assessment tools -- the
#   Collaborative Healthcare Interdisciplinary Relationship Planning
#   instrument and the Interprofessional Attitudes Scale -- following
#   didactic and clinical learning experiences in the United States. Journal
#   of Educational Evaluation for Health Professions, 16, 35. Harvard
#   Dataverse "Dataset 1. CHIRP response" and "Dataset 2. IPAS response"
#   (each with Data / Variable Labels / Variable Values sheets).
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# Students from 7 colleges were randomly assigned to complete either CHIRP or
# IPAS at baseline and after a didactic (2nd APD) or clinical (EPIC clinic)
# cohort. TWO output tables:
#   dennis_2019_chirp  b1..b14, CHIRP, 1 = I do not agree at all ... 5 = I
#     completely agree (Variable Values sheet). 529 forms; every form has its
#     own ID (the CHIRP file does not link a student's pre and post forms), so
#     `id` is the deposit ID and `wave` marks pre/post.
#   dennis_2019_ipas   A1..A27, IPAS, 1 = strongly disagree ... 7 = strongly
#     agree. 475 forms from 254 students: IDs repeat across sessions, so pre
#     and post are linked. A6 is stored REVERSE SCORED (deposit labels it
#     "REVERSE SCORED: It is not necessary for health care trainees to learn
#     together") and ships as stored, under the deposit's code A6_rev.
#   wave: "pre" for "Pre Overall", "post" for both post sessions; the session
#     itself is cov_session (Pre Overall / Post 2nd APD / Post EPIC clinic).
# Covariates: college/school, session. Averages (CHIRP_AVG, subscale
#   averages) are dropped.
#
# Item text: not shipped this run -- full stems are in the deposit's Variable
#   Labels sheets (CHIRP, IPAS), but neither instrument has a register row.
#   Cheap follow-up once one is written.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW_CHIRP = os.environ.get("DENNIS_CHIRP", "Dataset 1. CHIRP response.xlsx")
RAW_IPAS = os.environ.get("DENNIS_IPAS", "Dataset 2. IPAS response.xlsx")
COVS = ["cov_college", "cov_session"]


def build(path, session_col, items, permitted, name, n_rows, n_ids):
    d = pd.read_excel(path, sheet_name="Data")
    assert len(d) == n_rows and d["ID"].nunique() == n_ids, (len(d), d["ID"].nunique())
    d["id"] = d["ID"]
    d["cov_session"] = d[session_col]
    d["wave"] = d[session_col].map({"Pre Overall": "pre", "Post 2nd APD": "post", "Post EPIC clinic": "post"})
    d["cov_college"] = d["College"]
    assert d[["wave"] + COVS].notna().all().all()
    long = d[["id", "wave"] + COVS + items].melt(id_vars=["id", "wave"] + COVS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    assert set(long["resp"]) <= set(permitted)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + COVS]
    assert not long.duplicated(["id", "item", "cov_session"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    build(RAW_CHIRP, "SESSION", [f"b{i}" for i in range(1, 15)], [1, 2, 3, 4, 5], "dennis_2019_chirp", 529, 529)
    ipas = [f"A{i}" for i in range(1, 28)]
    ipas[5] = "A6_rev"
    build(RAW_IPAS, "EPIC_SESSION", ipas, [1, 2, 3, 4, 5, 6, 7], "dennis_2019_ipas", 475, 254)


if __name__ == "__main__":
    convert()
