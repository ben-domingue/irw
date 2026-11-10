#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/46v7bhb7sr/1
# DOI (data): 10.17632/46v7bhb7sr
# DOI (paper): 10.1007/s10734-022-00830-y
# Data: Clarke, O., Chan, W. Y. D., Bukuru, S., Logan, J. E., & Wong, R. (2022).
#   Assessing knowledge of and attitudes towards plagiarism and ability to
#   recognize plagiaristic writing among university students in Rwanda.
#   Higher Education, 85, 247-263. Mendeley Data file "UGHE Plagiarism Survey
#   DB.xlsx", sheet "clean" (data) and sheet "codebook".
# License: CC BY 4.0, verified on the Mendeley Data record (data_licence).
#
# Found by the repos sweep of 2026-11-10 (lane C, Step 2b recoverable_format).
#
# Checked against the paper (PMC9005340): 330 students (rows with an SN; nine
#   trailing rows are blank but for FinalYear and are dropped), mean age 25.2
#   (SD 4.6), knowledge score mean 83.1% (SD 16.3%), 248 high-knowledge
#   students, recognition mean 49.0%, 38 high recognisers -- all reproduce.
#
# THREE output tables, all scored by the depositors (codebook sheet):
#   clarke_2022_plagiarism_knowledge    K1..K10, 10 knowledge questions,
#     0 = incorrect, 1 = correct (the item mean equals the deposit's
#     KnowledgeScore on every row).
#   clarke_2022_plagiarism_attitude     A1..A10, 10 attitude statements,
#     dichotomised by the depositors: 1 = agree/strongly agree,
#     0 = disagree/strongly disagree. The 5-point responses are not deposited.
#   clarke_2022_plagiarism_recognition  Case1..Case5, five writing excerpts,
#     0 = incorrect, 1 = correct identification of plagiarism or not.
# Dropped: the score and level columns (composites), Case*P/Case*NP (the same
#   five answers re-split by whether the excerpt was plagiarised), Degree (the
#   codebook labels 1 = undergrad, 2 = graduate, but the paper's 193 bachelor's
#   students are code 2 and codes 3/4 are unlabelled, so the labels cannot be
#   trusted), and Comment (free text).
# Covariates: age (years), programme duration (years), current year of study,
#   final-year student (0 = no, 1 = yes).
# `id` is the deposit's SN (unique over the 330 respondents).
#
# Item text: NOT SHIPPED. The deposit has item codes only; the questions and
#   the five excerpts are printed in the paper (PMC9005340, Tables 2-4), which
#   is free to read (bronze) but carries no open licence.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CLARKE_RAW", "UGHE Plagiarism Survey DB.xlsx")
COVS = {"Age": "cov_age", "Duration": "cov_programme_years", "CurrentYear": "cov_year_of_study",
        "FinalYear": "cov_final_year"}
TABLES = {
    "clarke_2022_plagiarism_knowledge": [f"K{i}" for i in range(1, 11)],
    "clarke_2022_plagiarism_attitude": [f"A{i}" for i in range(1, 11)],
    "clarke_2022_plagiarism_recognition": [f"Case{i}" for i in range(1, 6)],
}


def convert():
    d = pd.read_excel(RAW, sheet_name="clean")
    d = d[d["SN"].notna()].copy()
    assert len(d) == 330 and d["SN"].is_unique
    k = TABLES["clarke_2022_plagiarism_knowledge"]
    full = d[k].notna().all(axis=1)
    assert ((d.loc[full, k].mean(axis=1) - d.loc[full, "KnowledgeScore"]).abs() < 1e-9).all()
    d["id"] = d["SN"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, items in TABLES.items():
        long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {0, 1}
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [0, 1] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
