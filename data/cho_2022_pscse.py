#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/SSQDDL
# DOI (data): 10.7910/DVN/SSQDDL
# DOI (paper): 10.3352/jeehp.2022.19.14
# Data: Cho, S., Lee, W., Kim, et al. (2022). Effect of online education on the
#   knowledge on, attitudes towards, and skills in patient safety for nursing
#   students in Korea. Journal of Educational Evaluation for Health
#   Professions, 19, 14. Harvard Dataverse "jeehp-19-14_add1.xlsx" (sheet
#   "coding"; Sheet2 maps A/B/C to the domains).
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# ONE output table:
#   cho_2022_pscse  revised Patient Safety Competency Self-Evaluation (PSCSE),
#     34 items: A1-A14 attitudes, B1-B12 skills, C1-C8 knowledge, 1 =
#     completely disagree ... 5 = totally agree (paper, Methods), given before
#     and after a synchronous online patient-safety course (wave pre/post).
#     One instrument, one table; the domain is in the item code prefix.
#   Checked: 110 nursing students, 99 women (gender 2), grade 1 = 39,
#     grade 2 = 33, 85 without prior patient-safety education (edu_exp 2):
#     all reproduce the paper. No missing cells.
# Covariates: gender, age, grade, prior patient-safety education.
# `id` is the deposit ID.
#
# Item text: not shipped -- codes only in the data file; the PSCSE stems are in
#   the deposit's Supplement 1 (.docx) but there is no register row.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CHO_RAW", "jeehp-19-14_add1.xlsx")
COVS = ["cov_gender", "cov_age", "cov_grade", "cov_prior_ps_education"]
NAME = "cho_2022_pscse"


def convert():
    d = pd.read_excel(RAW, sheet_name="coding")
    assert d.shape == (110, 73) and d["ID"].is_unique
    d["id"] = d["ID"]
    d["cov_gender"] = d["gender"].map({1: "male", 2: "female"})
    d["cov_age"] = d["age"]
    d["cov_grade"] = d["grade"]
    d["cov_prior_ps_education"] = d["edu_exp"].map({1: "yes", 2: "no"})
    assert (d["cov_gender"] == "female").sum() == 99 and (d["cov_prior_ps_education"] == "no").sum() == 85
    cols = [c for c in d.columns if c.startswith(("pre", "post"))]
    assert len(cols) == 68
    long = d[["id"] + COVS + cols].melt(id_vars=["id"] + COVS, var_name="col", value_name="resp")
    long["wave"] = long["col"].str.extract(r"^(pre|post)")[0]
    long["item"] = long["col"].str.replace(r"^(pre|post)", "", regex=True)
    long = long.dropna(subset=["resp"])
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + COVS]
    assert not long.duplicated(["id", "item", "wave"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in long["item"].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
