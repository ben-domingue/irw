#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/_/3834069
# DOI (paper): 10.1371/journal.pone.0162846
# Data: Wong, A., Lau, A. Y., Yang, J., ... & Mok, V. C. (2016). Neuropsychiatric
#   symptom clusters in stroke and transient ischemic attack by cognitive status
#   and stroke subtype: frequency and relationships with vascular lesions, brain
#   atrophy and amyloid. PLoS ONE, 11(9), e0162846. S1 Dataset.XLSX, sheet
#   "Database": 518 patients of the STRIDE cohort (Prince of Wales Hospital,
#   Hong Kong) given the Neuropsychiatric Inventory 3-6 months after a stroke
#   or TIA.
# License: CC BY 4.0 (PLOS article and its figshare supplement).
#
# Found by the repos sweep of 2026-11-10 (lane C, "neuropsychiatric inventory";
#   Step 2b recoverable_format).
#
# Checked against the paper: N = 518, age SD 11.0 (mean 71.4 here vs 71.1 in
#   the text), 7 patients with any euphoria (NPI06) -- the paper's n = 7.
#   The text says "244 (51%) were female"; Sex = 2 holds 264 rows, which is
#   the 51%, so 2 = female and the 244 is a typo in the paper.
#
# ONE output table:
#   wong_2016_npi_stroke  NPI01..NPI12, the 12 NPI domains in the standard
#     order (1 delusions, 2 hallucinations, 3 agitation/aggression,
#     4 depression/dysphoria, 5 anxiety, 6 elation/euphoria, 7 apathy,
#     8 disinhibition, 9 irritability, 10 aberrant motor behaviour,
#     11 night-time behaviour, 12 appetite/eating; the paper's Table 2
#     numbering). Each value is the NPI domain score as the paper defines it,
#     "frequency (0-4) x severity (0-3)", so the possible values are
#     0,1,2,3,4,6,8,9,12. Rated by clinicians from caregiver interview.
#   Dropped: 9999 (missing; 27 cells over 22 patients -- NPItotal treats them
#     as 0, so they are not responses) and one 5 on NPI04, which no
#     frequency x severity product can give (a data-entry error).
# Covariates: sex (1 = male, 2 = female, per the check above), age, years of
#   education, MMSE total. The clinical and imaging columns (hypertension,
#   diabetes, NIHSS, white-matter score, atrophy ratings, CDR, stroke subtype)
#   are numeric codes the deposit does not label, so they are not carried.
#   NPItotal and the cluster scores are composites and are dropped.
# `id` is SubjectNo (unique).
#
# Item text: NOT SHIPPED. The NPI (Cummings 1994) is copyrighted; the deposit
#   carries domain codes only.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("WONG_RAW", "S1 Dataset.XLSX")
ITEMS = [f"NPI{i:02d}" for i in range(1, 13)]
VALID = [0, 1, 2, 3, 4, 6, 8, 9, 12]
COVS = {"Sex": "cov_sex", "Age": "cov_age", "Educationyear": "cov_education_years", "MMSEtotal": "cov_mmse"}


def convert():
    d = pd.read_excel(RAW, sheet_name="Database")
    assert d.shape == (518, 38), d.shape
    assert d["SubjectNo"].is_unique
    assert (d["Sex"] == 2).sum() == 264
    assert (d["NPI06"].between(1, 12)).sum() == 7
    d["id"] = d["SubjectNo"]
    d = d.rename(columns=COVS)
    d["cov_sex"] = d["cov_sex"].map({1: "male", 2: "female"})
    covs = list(COVS.values())
    long = d[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    n_missing = (long["resp"] == 9999).sum()
    n_bad = (~long["resp"].isin(VALID + [9999]) & long["resp"].notna()).sum()
    assert n_missing == 27 and n_bad == 1, (n_missing, n_bad)
    long = long[long["resp"].isin(VALID)].copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: VALID for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    name = "wong_2016_npi_stroke"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
