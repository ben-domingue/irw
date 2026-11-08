#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0235305
# DOI: 10.1371/journal.pone.0235305
# Paper: Perez-Fuentes MC, Molero Jurado MM, Martos Martinez A, Gazquez
#   Linares JJ (2020). Threat of COVID-19 and emotional state during
#   quarantine: Positive and negative affect as mediators in a cross-sectional
#   study of the Spanish population. PLoS ONE 15(6): e0235305.
# Data: PLOS Supporting Information S1 Data (journal.pone.0235305.s002, .sav
#   with Spanish value labels). 1,014 Spanish adults, CAWI survey in the first
#   week of lockdown, March 2020.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# ONE output table:
#   perez_fuentes_2020_affect_balance  Affect Balance Scale (Spanish
#     adaptation), EBA1-EBA18, 1 little or never, 2 sometimes, 3 a lot or
#     usually. Positive items 3,5,7,9,12,13,15,16,18 and negative items
#     1,2,4,6,8,10,11,14,17 are scored separately (no reversal); their sums
#     equal the deposit's EBApos and EBAneg on every row (asserted).
# Checks: N = 1,014, 681 women, mean age 40.87 as in the paper (asserted).
# Dropped: EVEA mood scale (EVEA2 and EVEA8, two anger-hostility items,
#   are identical on every row, so one item's answers are lost, and the
#   deposit's 1-10 range departs from the paper's 0-10); the 5-item
#   COVID-19 threat questionnaire (BIP-Q: the item sum is the deposited
#   total and the deposit does not show whether the control items were
#   reversed before entry; dropped under the 2026-11-08 rule, and thin).
# Covariates: age, sex, marital status, education, dependent children,
#   COVID-19 case in close environment (value labels, translated).
# `id` is the row index (the deposit carries no identifier).
#
# Item text: NOT SHIPPED. The ABS is a published instrument; the deposit has
#   no wording.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0235305.s002"
RAW = os.environ.get("PEREZFUENTES2020_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
POS = [3, 5, 7, 9, 12, 13, 15, 16, 18]
NEG = [1, 2, 4, 6, 8, 10, 11, 14, 17]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_perezfuentes2020_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, meta = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df, meta


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(values)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df, meta = load()
    assert len(df) == 1014
    assert (df["Sex"] == 1).sum() == 681 and round(df["Age"].mean(), 2) == 40.87
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Age"]
    df["cov_sex"] = df["Sex"].map({0: "male", 1: "female"})
    df["cov_marital_status"] = df["MaritalStatus"].map({0: "single", 1: "married", 2: "divorced", 3: "widowed"})
    df["cov_education"] = df["EduLevel"].map({0: "none", 1: "primary", 2: "secondary", 3: "higher"})
    df["cov_children"] = df["Children"].map({0: "no", 1: "yes"})
    df["cov_covid_case_close"] = df["COVID_PosCase"].map({0: "no", 1: "yes"})
    covs = ["cov_age", "cov_sex", "cov_marital_status", "cov_education", "cov_children", "cov_covid_case_close"]
    assert meta.variable_value_labels["Sex"] == {0.0: "hombre", 1.0: "mujer"}

    assert (df[[f"EBA{i}" for i in POS]].sum(axis=1) == df["EBApos"]).all()
    assert (df[[f"EBA{i}" for i in NEG]].sum(axis=1) == df["EBAneg"]).all()
    assert (df["EVEA2"] == df["EVEA8"]).all()  # the reason EVEA is not shipped
    items = [f"EBA{i}" for i in range(1, 19)]
    out = df.rename(columns={c: f"aba{int(c[3:]):02d}" for c in items})
    save(out, covs, [f"aba{i:02d}" for i in range(1, 19)], "perez_fuentes_2020_affect_balance", [1, 2, 3])


if __name__ == "__main__":
    convert()
