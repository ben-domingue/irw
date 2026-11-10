#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ARRAGK
# DOI (data): 10.7910/DVN/ARRAGK
# DOI (paper): 10.3352/jeehp.2017.14.8
# Data: Shawahna, R., Khaskiyyi, M., Abdo, H., Msarwe, Y., Odeh, R., &
#   Salame, S. (2017). Palestinian pharmacists' knowledge of issues related to
#   using psychotropic medications in older people: a cross-sectional study.
#   Journal of Educational Evaluation for Health Professions, 14, 8. Harvard
#   Dataverse file "jeehp_14_8_April_24_rawdata.xlsx" (400 pharmacists; the
#   19 statements are the column headers, answers stored as True / False /
#   "I don't know").
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) in a Harvard Dataverse search of JEEHP deposits
#   during the repos sweep.
#
# ONE output table:
#   shawahna_2017_psychotropic  19 true/false knowledge statements on
#     psychotropic medication use in older people, scored 1 = correct,
#     0 = incorrect; resp_raw keeps the answer given ("True"/"False").
#   Answer key: every statement is true except the olanzapine dose (50-100
#     mg/day is false). The paper marks correct answers in bold in Table 2,
#     which the web text does not preserve; the key was checked by rebuilding
#     the paper's own score (+1 correct, -0.5 wrong, 0 don't know, as % of 19):
#     median 55.3% (paper 55.3%) and 280 pharmacists >= 50% (paper Table 3:
#     280). Without the olanzapine exception neither figure reproduces.
#   "I don't know" (843 answers, plus 5 cells holding a mangled "I don't
#     know" string) is a non-response under datastandard.md and is dropped,
#     not scored 0, although the paper gives it 0 points.
#   Item codes: q01..q19 in the deposit's column order, which is not the
#     paper's Table 2 order (the deposit groups differently); the map from
#     code to statement is ITEM_TEXT below, taken from the column headers.
# Covariates (all banded as deposited): age (<35 / >=35), gender, place of
#   residence, degree, years in practice, practice setting, took a course on
#   psychotropic drugs. The banded Score column is a composite and dropped.
# `id` is the row index: "Participant number" repeats once (399 unique of
#   400 rows), and the paper reports 400 pharmacists.
#
# Item text: NOT SHIPPED. The statements are the deposit's column headers, but
#   the test is Wauters et al.'s (Belgium) nurse knowledge test, adapted; no
#   register row, so silence holds. Headers kept in ITEM_TEXT for a later pass.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SHAWAHNA_RAW", "jeehp_14_8_April_24_rawdata.xlsx")
COVS = {"Age (years)": "cov_age_band", "Gender": "cov_gender", "Place of residence": "cov_residence",
        "Degree in pharmacy": "cov_degree", "Number of years in practice": "cov_years_practice",
        "Practice settings": "cov_practice_setting",
        "Had a course on psychotropic drugs during pharmacy degree program": "cov_psychotropic_course"}


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (400, 28), d.shape
    stmts = list(d.columns[8:27])
    assert len(stmts) == 19 and d.columns[27] == "Score"
    codes = [f"q{k:02d}" for k in range(1, 20)]
    key = {c: ("False" if "olanzapine" in s else "True") for c, s in zip(codes, stmts)}
    assert list(key.values()).count("False") == 1
    global ITEM_TEXT
    ITEM_TEXT = dict(zip(codes, stmts))
    d = d.rename(columns=dict(zip(stmts, codes))).rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)
    covs = list(COVS.values())
    for c in codes:
        d[c] = d[c].astype(str)
    # reproduce the paper's score before scoring anything
    corr = sum((d[c] == key[c]).astype(int) for c in codes)
    wrong = sum(d[c].isin(["True", "False"]) & (d[c] != key[c]) for c in codes)
    pct = (corr - 0.5 * wrong) / 19 * 100
    assert round(pct.median(), 1) == 55.3 and (pct >= 50).sum() == 280
    assert ((pct >= 50) == (d["Score"] == "≥ 50%")).all()
    long = d[["id"] + covs + codes].melt(id_vars=["id"] + covs, var_name="item", value_name="resp_raw")
    long = long[long["resp_raw"].isin(["True", "False"])].copy()
    long["resp"] = (long["resp_raw"] == long["item"].map(key)).astype(int)
    long = long[["id", "item", "resp", "resp_raw"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1] for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    name = "shawahna_2017_psychotropic"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


ITEM_TEXT = {}

if __name__ == "__main__":
    convert()
