#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.19174205
# DOI: 10.1371/journal.pone.0268232 (paper); data 10.6084/m9.figshare.19174205
# Paper: Yeo ZZ, Suarez L (2022). Validation of the mental health
#   continuum-short form: The bifactor model of emotional, social, and
#   psychological well-being. PLoS ONE 17(5): e0268232.
# Data: figshare 19174205, MasterFile_CLEAN.xlsx; 557 adults living in
#   Singapore (300) or Australia (257), online survey.
# License: CC BY 4.0 (figshare record).
# Codebook: none; the workbook carries each answer both as the text option
#   chosen and as the scored number, so codes are checked against labels.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# THREE output tables (numeric columns as scored by the deposit):
#   yeo_2022_mhcsf  Mental Health Continuum-Short Form, mhc1..mhc14, 0 never
#     .. 5 every day (sum = mhc_total on every row).
#   yeo_2022_who5   WHO-5, 0-5 (4 x sum = WHO_SCORE on every row).
#   yeo_2022_hads   HADS, A1..A6, A7_R, D1, D2_R, D3, D4_R..D7_R, 0-3 AS
#     SCORED: the _R items are the reverse-keyed ones, already scored in
#     symptom direction (cross-tabulated against the text answers, e.g. A7_R
#     "Definitely [can sit at ease]" = 0); subscale sums equal the deposited
#     Anxiety/Depression scores on every row.
# Dropped: the text-answer duplicates, the single self-rating of mental
#   health, derived MHC diagnosis/affect/function indicators, free-text
#   "other" answers.
# Covariates: age, gender (as chosen), country of residence, population
#   group (no disability / recovering from mental health issues / disability).
# `id` = row index.
#
# Item text: NOT SHIPPED. The text-option columns carry the response labels
#   for every item and the HADS column headers abbreviate the stems; the
#   MHC-SF, WHO-5 and HADS stems are not deposited in full (HADS is a
#   register block).

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/34067789"
RAW = os.environ.get("YEO2022_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_yeo2022_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert len(df) == 557
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_age"] = df["Whatisyourage"]
    df["cov_gender"] = df["WhatisyourgenderSelectedChoice"]
    df["cov_residence"] = df["WhatisyourcurrentcountryofresidenceSelectedChoice"]
    df["cov_population_group"] = df["Whatisyourcurrentpopulationgroup"]
    covs = ["cov_age", "cov_gender", "cov_residence", "cov_population_group"]
    mhc = [f"mhc{i}" for i in range(1, 15)]
    who = [f"WHO{i}" for i in range(1, 6)]
    anx = ["A1", "A2", "A3", "A4", "A5", "A6", "A7_R"]
    dep = ["D1", "D2_R", "D3", "D4_R", "D5_R", "D6_R", "D7_R"]
    assert (df[mhc].sum(axis=1) == df["mhc_total"]).all()
    assert (df[who].sum(axis=1) * 4 == df["WHO_SCORE"]).all()
    assert (df[anx].sum(axis=1) == df["Anxiety_SCORE"]).all()
    assert (df[dep].sum(axis=1) == df["Depression_SCORE"]).all()
    save(df, covs, mhc, "yeo_2022_mhcsf", range(0, 6))
    save(df, covs, who, "yeo_2022_who5", range(0, 6))
    save(df, covs, anx + dep, "yeo_2022_hads", range(0, 4))


if __name__ == "__main__":
    convert()
