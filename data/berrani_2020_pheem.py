#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/MSPVKH
# DOI (data): 10.7910/DVN/MSPVKH
# DOI (paper): 10.3352/jeehp.2020.17.4
# Data: Berrani, H., Abouqal, R., & Izgua, A. T. (2020). Moroccan residents'
#   perceptions of the hospital learning environment measured with the
#   French version of the Postgraduate Hospital Educational Environment
#   Measure. Journal of Educational Evaluation for Health Professions, 17, 4.
#   Harvard Dataverse "Dataset 1. Data file and data dictionary" (Sheet1).
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# ONE output table:
#   berrani_2020_pheem  PHEEM1..PHEEM40, French PHEEM, 0 = strongly disagree,
#     1 = disagree, 2 = uncertain, 3 = agree, 4 = strongly agree (paper,
#     Methods). Items 7, 8, 11 and 13 are negatively worded; the deposit's
#     columns say "negatif" and the item sum equals the deposit's scoretotal
#     on every complete row, so those four are stored ALREADY REVERSED
#     (scored), and ship as stored. 11 blank cells are dropped.
#   Checked: 255 residents at 6 hospitals in Rabat, Jan-Jun 2017; item sums
#     reproduce the deposit total exactly.
# Covariates: age, sex, marital status, number of children, prior practice
#   as a general practitioner, age at start of residency, residency level,
#   specialty (unlabeled code), hospital. Value labels are taken from the
#   deposit's own column names (e.g. "sexeM0F1", "...Celibataire0marie1
#   divorce2"); "#NULL!" cells are left empty.
# Dropped: score totals, classifications and the confidence-limit columns.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Codes only in the deposit; PHEEM (Roff et al.
#   2005) and its French version have no register row.

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
    sub = d[["id"] + covs + items].rename(columns=dict(zip(items, codes)))
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[~long["resp"].isin(drop_values)]
    assert (long["resp"] == np.floor(long["resp"])).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted), set(long["resp"])
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

RAW = os.environ.get("BERRANI_RAW", "Dataset 1. Data file and data dictionary.xlsx")
COVS = {"Age": "cov_age", "sexeM0F1": "cov_sex",
        "SituationmaritaleCelibataire0marie1divorce2": "cov_marital_status",
        "nombredenfants": "cov_children",
        "Avezvousexercecommemedecingeneralisteavantleresidanatoui0non1": "cov_prior_gp_practice",
        "Agedebutresidanat": "cov_age_start_residency", "ResidencyLevel": "cov_residency_level",
        "Specialty": "cov_specialty",
        "HopitalHER0Maternites1avicenne2spécialités3INO4dentaire6": "cov_hospital"}
# value labels spelled out in the deposit's own column names
LABELS = {"cov_sex": {0: "male", 1: "female"}, "cov_marital_status": {0: "single", 1: "married", 2: "divorced"},
          "cov_prior_gp_practice": {0: "yes", 1: "no"},
          "cov_hospital": {0: "HER", 1: "Maternites", 2: "Avicenne", 3: "Specialites", 4: "INO", 6: "dentaire"}}


def convert():
    d = pd.read_excel(RAW, sheet_name="Sheet1")
    assert d.shape == (255, 62)
    items = [c for c in d.columns if str(c).startswith("PHEEM")]
    assert len(items) == 40
    codes = [f"PHEEM{k}" for k in range(1, 41)]
    x = d[items].apply(pd.to_numeric, errors="coerce")
    full = x.notna().all(axis=1)
    assert (x[full].sum(axis=1) == pd.to_numeric(d.loc[full, "scoretotal"])).all()
    d["id"] = range(1, len(d) + 1)
    for s, t in COVS.items():
        d[t] = pd.to_numeric(d[s], errors="coerce")
    for t, lab in LABELS.items():
        assert set(d[t].dropna()) <= set(lab), (t, set(d[t].dropna()))
        d[t] = d[t].map(lab)
    write(d, items, [0, 1, 2, 3, 4], "berrani_2020_pheem", list(COVS.values()), codes=codes)


if __name__ == "__main__":
    convert()
