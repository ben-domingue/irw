#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/AWC1IP
# DOI (data): 10.7910/DVN/AWC1IP
# DOI (paper): 10.3352/jeehp.2021.18.6
# Data: Elnaem, M. H., Akkawi, M. E., Nazar, N. I. M., Ab Rahman, N. S., &
#   Mohamed, M. H. N. (2021). Malaysian pharmacy students' perspectives on the
#   virtual objective structured clinical examination during the coronavirus
#   disease 2019 pandemic. Journal of Educational Evaluation for Health
#   Professions, 18, 6. Harvard Dataverse "Dataset 1. Raw response data of the
#   questionnaire on the virtual objective structured clinical examination"
#   (Google Forms export, sheet "Form Responses 1").
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# ONE output table:
#   elnaem_2021_virtual_osce  17 statements about the virtual OSCE (q01..q17,
#     the deposit's numbered questions in order), answered as text:
#     Strongly disagree = 1, Disagree = 2, Neutral = 3, Agree = 4, Strongly
#     Agree = 5. resp_raw keeps the text. 231 pharmacy students (years 3-4).
# Covariates: year of study, gender, course(s) the answers apply to (as the
#   form's multi-select string), interest in clinical pharmacy courses and as
#   a career (5-level text, kept as text).
# Dropped: timestamp, free-text comments. `id` is the row index.
#
# Item text: not shipped -- the full statements are the column headers, but
#   there is no register row for this questionnaire. Cheap follow-up.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ELNAEM_RAW", "Dataset 1. Raw response data of the questionnaire.xlsx")
NAME = "elnaem_2021_virtual_osce"
CODE = {"Strongly disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}
COVS = ["cov_year_of_study", "cov_gender", "cov_courses", "cov_interest_courses", "cov_interest_career"]


def convert():
    d = pd.read_excel(RAW, sheet_name="Form Responses 1")
    assert d.shape == (231, 24)
    cols = list(d.columns)
    items = cols[6:23]
    assert [c.split(".")[0] for c in items] == [str(i) for i in range(1, 18)]
    d["id"] = range(1, len(d) + 1)
    for src, dst in zip(cols[1:6], COVS):
        d[dst] = d[src]
    codes = [f"q{i:02d}" for i in range(1, 18)]
    long = d[["id"] + COVS + items].rename(columns=dict(zip(items, codes))).melt(
        id_vars=["id"] + COVS, var_name="item", value_name="resp_raw").dropna(subset=["resp_raw"])
    long["resp_raw"] = long["resp_raw"].str.strip()
    assert set(long["resp_raw"]) <= set(CODE), set(long["resp_raw"]) - set(CODE)
    long["resp"] = long["resp_raw"].map(CODE)
    long = long[["id", "item", "resp", "resp_raw"] + COVS]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
