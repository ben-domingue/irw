#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/3JDN9S
# DOI (data): 10.7910/DVN/3JDN9S
# DOI (paper): 10.3352/jeehp.2023.20.14
# Data: Kim, G. M., Kim, Y., & Kim, S. K. (2023). Factors influencing the
#   learning transfer of nursing students in a non-face-to-face educational
#   environment during the COVID-19 pandemic in Korea: a cross-sectional study
#   using structural equation modeling. Journal of Educational Evaluation for
#   Health Professions, 20, 14. Harvard Dataverse "jeehp-20-14-dataset1.xlsx".
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# 218 nursing students at Gangneung Wonju National University, Feb-Mar 2022.
# Checked: N = 218; 183 women (성별 2) = 83.9%; 97 fourth-years = 44.5%; both
# as in the paper. Scale averages stored in the deposit equal the item means
# exactly. THREE output tables (paper, Data sources/measurement):
#   kim_2023_learning_immersion     몰입1-29 -> immersion1..29, learning
#     immersion (Kim et al.), 1-5.
#   kim_2023_learning_selfefficacy  효능1-10 -> selfefficacy1..10, learning
#     self-efficacy (Ayres; Korean by Park & Kweon), 1-7.
#   kim_2023_learning_transfer      학습전이1-4 -> transfer1..4, learning
#     transfer (Lee), 1-5.
#   1 = extremely disagree ... 5 (or 7) = extremely agree. No missing cells.
# NOT shipped from the same file:
#   - 주도1-22, self-directed learning ability (Guglielmino, modified by Kim &
#     Lee): the stored average equals the raw item mean and no item correlates
#     negatively with the rest, so any negatively worded items were stored
#     already reversed, and which ones cannot be verified (pre-scored-reversal
#     rule). Held in the hand-off.
#   - 만족1-17: the paper's satisfaction scale has 15 items, the file 17.
#   - 전이동기1-10 (transfer motivation, 1-7): not described in the paper.
# Covariates: age, sex, school year. Other background columns are unlabeled
#   codes and are dropped.
#
# Item text: not shipped -- Korean short codes only.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KIM23_RAW", "jeehp-20-14-dataset1.xlsx")
COVS = ["cov_age", "cov_sex", "cov_school_year"]
SCALES = [("몰입", 29, "immersion", 5, "kim_2023_learning_immersion"),
          ("효능", 10, "selfefficacy", 7, "kim_2023_learning_selfefficacy"),
          ("학습전이", 4, "transfer", 5, "kim_2023_learning_transfer")]


def convert():
    d = pd.read_excel(RAW).iloc[1:].reset_index(drop=True)  # first data row is blank
    assert len(d) == 218 and d["ID"].is_unique
    d["id"] = d["ID"].astype(int)
    d["cov_age"] = d["연령"]
    d["cov_sex"] = d["성별"].map({1: "male", 2: "female"})
    assert (d["cov_sex"] == "female").sum() == 183
    d["cov_school_year"] = d["학년"]
    for prefix, n, stem, top, name in SCALES:
        src = [f"{prefix}{i}" for i in range(1, n + 1)]
        codes = [f"{stem}{i}" for i in range(1, n + 1)]
        sub = d[["id"] + COVS + src].rename(columns=dict(zip(src, codes)))
        long = sub.melt(id_vars=["id"] + COVS, var_name="item", value_name="resp").dropna(subset=["resp"])
        permitted = list(range(1, top + 1))
        assert set(long["resp"]) <= set(permitted)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + COVS]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: permitted for c in codes})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
