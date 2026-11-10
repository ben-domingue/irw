#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/UQP3PI
# DOI (data): 10.7910/DVN/UQP3PI
# DOI (paper): 10.3352/jeehp.2024.21.37
# Data: Panthumas, S., Zaw, K., & Kittipichai, W. (2024). Validation of the
#   21st Century Skills Assessment Scale for public health students in
#   Thailand: a methodological study. Journal of Educational Evaluation for
#   Health Professions, 21, 37. Harvard Dataverse "jeehp-21-37-dataset 1.xlsx",
#   sheet "Data" (all 727; sheets Dataset1/Dataset2 are its EFA/CFA halves).
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper: 727 undergraduates, 638 women (87.8%), years
#   1-4 = 190/180/197/160 -- all reproduce (Sex 2 = female, Year as coded).
#
# ONE output table:
#   panthumas_2024_21csas  21 items, 1 = strongly disagree ... 5 = strongly
#     agree (paper, Methods): learning and innovation (CI1-3 creativity, CP1-3
#     critical thinking, CC1-4 communication/collaboration), information,
#     media and technology (IMT1-5), life and career (IS1-3, SC1-3). One
#     instrument, kept in one table with the deposit's item codes.
# Covariates: sex, year of study, university (unlabeled code 1-4 as
#   deposited), analysis subsample (dataset 1 = EFA, 2 = CFA).
# `id` is the deposit's ID (unique).
#
# Item text: NOT SHIPPED. Codes only in the deposit; items are in the paper.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("PANTHUMAS_RAW", "jeehp-21-37-dataset 1.xlsx")
ITEMS = ["CI1", "CI2", "CI3", "CP1", "CP2", "CP3", "CC1", "CC2", "CC3", "CC4", "IMT1", "IMT2", "IMT3", "IMT4",
         "IMT5", "IS1", "IS2", "IS3", "SC1", "SC2", "SC3"]


def convert():
    d = pd.read_excel(RAW, sheet_name="Data")
    assert d.shape == (727, 26) and d["ID"].is_unique
    assert (d["Sex"] == 2).sum() == 638
    d["id"] = d["ID"]
    d["cov_sex"] = d["Sex"].map({1: "male", 2: "female"})
    d["cov_year"] = d["Year"]
    d["cov_university"] = d["Univeraity"]
    d["cov_subsample"] = d["dataset"].map({1: "EFA", 2: "CFA"})
    covs = ["cov_sex", "cov_year", "cov_university", "cov_subsample"]
    assert d[covs].notna().all().all()
    long = d[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    name = "panthumas_2024_21csas"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
