#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0313426
# DOI: 10.1371/journal.pone.0313426
# Paper: Knedlikova L, Dedkova L, Kolar ... Danhofer P (2024). The impact of
#   the COVID-19 pandemic on stress and coping in parents of children with
#   Autism Spectrum Disorder. PLoS ONE 19(11): e0313426.
# Data: PLOS SI S1 (journal.pone.0313426.s001, labelled .sav), 344 Czech
#   parents: 44 of children with ASD, 300 controls (Group), online 2022-23.
# License: CC BY 4.0 (the article and its SI).
# Codebook: the .sav variable and value labels (Czech item wording).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# TWO output tables, Adult Self-Report RSQ-COVID-19 (Connor-Smith & Compas):
#   knedlikova_2024_rsq_stressors  PRSQa..PRSQn, 12 stressor items (k and l
#     were omitted from the survey by a technical error, per the paper),
#     1 not at all .. 4 very stressful.
#   knedlikova_2024_rsq_coping     PRSQ01..PRSQ57 as deposited, 53 items (the 1-4
#     Never/Rarely/Sometimes/Often items; 10, 37, 43 and 45 have no 1-4 column
#     in the deposit, only check-all lists for 37/43/45), raw.
# Dropped: the single perceived-control item (PRSQcon), the yes/no
#   check-all follow-ups (PRSQ07a.., PRSQ17a.., etc.: unchecked and not shown
#   can't be told apart, and several are conditional), factor scores, the
#   survey date, and the deposit's ID (16-digit panel numbers) for the row
#   index.
# Covariates (value labels as text): group (ASD / control), matched-subsample
#   flag, municipality size, highest parental education, child age, child
#   gender, household finances, most severe COVID-19 course in the family.
#
# Item text: NOT SHIPPED. Czech wording is in the .sav variable labels, but
#   the RSQ is Vanderbilt's (Compas lab) and distributed on request; check
#   the register before shipping.

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0313426.s001"
RAW = os.environ.get("KNEDLIKOVA2024_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}

ENGLISH = {
    "cov_group": {1: "ASD", 2: "control"},
    "cov_matched_group": {1: "ASD", 2: "matched control"},
    "cov_municipality_size": {1: "<5,000", 2: "5,000-100,000", 3: ">100,000"},
    "cov_child_gender": {1: "boy", 2: "girl"},
}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_knedlikova2024_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, meta = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df, meta


def save(df, covs, items, name):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= {1, 2, 3, 4}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df, meta = load()
    assert len(df) == 344
    vl = meta.variable_value_labels
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    src = {"cov_group": "Group", "cov_matched_group": "Matched_groups",
           "cov_municipality_size": "Municipality", "cov_child_gender": "C_gender"}
    for cov, col in src.items():
        df[cov] = df[col].map(ENGLISH[cov])
    df["cov_parent_education"] = df["P_educ"].map(vl["P_educ"])
    df["cov_finances"] = df["Finances"].map(vl["Finances"])
    df["cov_covid_course"] = df["COVID"].map(vl["COVID"])
    df["cov_child_age"] = df["C_age"]
    assert (df["cov_group"] == "ASD").sum() == 44
    covs = ["cov_group", "cov_matched_group", "cov_municipality_size", "cov_parent_education",
            "cov_child_age", "cov_child_gender", "cov_finances", "cov_covid_course"]
    stress = [c for c in df.columns if re.fullmatch(r"PRSQ[a-n]", c)]
    coping = [c for c in df.columns if re.fullmatch(r"PRSQ\d\d", c)]
    assert len(stress) == 12 and "PRSQk" not in stress and "PRSQl" not in stress
    assert len(coping) == 53, len(coping)
    save(df, covs, stress, "knedlikova_2024_rsq_stressors")
    save(df, covs, coping, "knedlikova_2024_rsq_coping")


if __name__ == "__main__":
    convert()
