#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0137101
# DOI: 10.1371/journal.pone.0137101
# Paper: Zhang Y, Zhang J, Zhu S, Du C, Zhang W (2015). Prevalence and
#   predictors of somatic symptoms among child and adolescents with probable
#   posttraumatic stress disorder: A cross-sectional study conducted in 21
#   primary and secondary schools after an earthquake. PLoS ONE 10(9):
#   e0137101.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0137101.s001,
#   .sav with variable and value labels). 3,053 pupils aged 8-19 in Baoxing
#   County, three months after the 2013 Lushan earthquake.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 6.
#
# TWO output tables:
#   zhang_2015_phq13  PHQ-15 without the menstrual and sexuality items (the
#     paper's PHQ-13), p1-p13, 0 not bothered, 1 a little, 2 a lot.
#   zhang_2015_earthquake_exposure  the 8 earthquake-related experiences of
#     Table 1 (m2-m6, m8, m9, m12), recoded 1 = yes, 0 = no (deposited
#     1 = yes, 2 = no).
# Check: on the 93% of rows with all 13 PHQ items answered the item sum
#   equals the deposit's PHQ13score (asserted); 1,545 female (paper 1,545).
# Dropped: CRIESscore (total only). Covariates gender, age, ethnicity (Han /
#   minority), from the value labels.
# `id` is the row index (the deposit carries no identifier).
#
# Item text: NOT SHIPPED. PHQ-15 is a published instrument; the variable
#   labels carry the English symptom names only.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0137101.s001"
RAW = os.environ.get("ZHANG2015_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
EXPO = ["m2", "m3", "m4", "m5", "m6", "m8", "m9", "m12"]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_zhang2015_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


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
    df = load()
    assert df.shape == (3053, 26), df.shape
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["gender"].map({1: "male", 2: "female"})
    df["cov_age"] = df["age"]
    df["cov_ethnicity"] = df["ethnicity"].map({1: "Han", 2: "minority"})
    assert (df["cov_gender"] == "female").sum() == 1545
    covs = ["cov_gender", "cov_age", "cov_ethnicity"]

    phq_src = [f"p{i}转化" for i in range(1, 14)]
    phq = [f"p{i}" for i in range(1, 14)]
    df = df.rename(columns=dict(zip(phq_src, phq)))
    full = df[phq].notna().all(axis=1)
    assert (df.loc[full, phq].sum(axis=1) == df.loc[full, "PHQ13score"]).all()
    save(df, covs, phq, "zhang_2015_phq13", [0, 1, 2])

    for c in EXPO:
        assert set(df[c].dropna()) <= {1, 2}
        df[c] = df[c].map({1: 1, 2: 0})
    save(df, covs, EXPO, "zhang_2015_earthquake_exposure", [0, 1])


if __name__ == "__main__":
    convert()
