#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/1Q5IVY
# DOI (data): 10.7910/DVN/1Q5IVY
# DOI (paper): 10.3352/jeehp.2026.23.22
# Data: Jongchidklang, W., Phonphithak, S., & Amornritvanich, P. (2026).
#   Development and psychometric validation of the Thai AI Literacy Scale for
#   Nursing Students (TAILS-NS) in Thailand: a cross-sectional observational
#   study. Journal of Educational Evaluation for Health Professions, 23, 22.
#   Harvard Dataverse: "Dataset 1" (development sample, n = 410) and
#   "Dataset 2" (independent validation sample, n = 157), same 48 columns.
#   "Dataset 3" (65 test-retest pairs, a subset re-tested) is not used.
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection
#   (flag good).
#
# Checked against the paper (Table 1): development sample 410, female 370
#   (90.2%), male 25, LGBTQ+ 14, not specified 1, year 1 = 237 -- all
#   reproduce with gender codes 2/1/3/9.
#
# TWO output tables, each merging the two samples (same instrument, same
#   columns, per the paper's design); cov_study = development / validation and
#   the validation ids are offset by 10,000:
#   jongchidklang_2026_tails_knowledge  know1..know15, the 15-item AI
#     knowledge test, 0/1 (1 = correct).
#   jongchidklang_2026_tails_ns  a1..e5, the 25 Likert items, 1-5. The paper
#     reports 6 EFA domains (awareness, skills, ethics and professionalism,
#     positive attitude, AI anxiety, readiness); the deposit's a-e letter
#     blocks are kept as item codes.
# Covariates: study year (1-4), age group (as deposited), and, for the
#   development sample only, gender and home region with the paper's labels.
#   The validation sample codes gender 1/2/3/4 with 145 in code 1 -- not the
#   development coding -- so gender, region and the three AI-experience codes
#   are left empty for its rows rather than guessed. The AI experience, skill
#   and training codes are unlabeled in both files and are not carried.
#
# Item text: NOT SHIPPED. The deposit holds codes only; the items are in the
#   paper's supplement.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW1 = os.environ.get("TAILS_RAW1", "dataset1.csv")
RAW2 = os.environ.get("TAILS_RAW2", "dataset2.csv")
GENDER = {2: "female", 1: "male", 3: "LGBTQ+", 9: "not specified"}
REGION = {4: "Northeastern", 6: "Eastern/Western", 2: "Central", 5: "Southern", 1: "Bangkok and vicinity",
          3: "Northern"}
KNOW = [f"know{k}" for k in range(1, 16)]
LIK = [f"{b}{k}" for b in "abcde" for k in range(1, 6)]


def load():
    a = pd.read_csv(RAW1)
    b = pd.read_csv(RAW2)
    assert a.shape == (410, 48) and b.shape == (157, 48)
    assert list(a.columns) == list(b.columns)
    assert a["gender"].value_counts().to_dict() == {2: 370, 1: 25, 3: 14, 9: 1}
    assert (a["region"] == 4).sum() == 174 and (a["year"] == 1).sum() == 237
    a["cov_study"] = "development"
    a["cov_gender"] = a["gender"].map(GENDER)
    a["cov_region"] = a["region"].map(REGION)
    b["cov_study"] = "validation"
    b["cov_gender"] = pd.NA
    b["cov_region"] = pd.NA
    b["id"] = b["id"] + 10000
    d = pd.concat([a, b], ignore_index=True)
    assert d["id"].is_unique
    d["cov_year"] = d["year"]
    d["cov_age_group"] = d["age_group"]
    return d


def write(d, items, permitted, name, covs):
    long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted), set(long["resp"])
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    d = load()
    covs = ["cov_study", "cov_year", "cov_age_group", "cov_gender", "cov_region"]
    os.makedirs(OUT_DIR, exist_ok=True)
    write(d, KNOW, [0, 1], "jongchidklang_2026_tails_knowledge", covs)
    write(d, LIK, [1, 2, 3, 4, 5], "jongchidklang_2026_tails_ns", covs)


if __name__ == "__main__":
    convert()
