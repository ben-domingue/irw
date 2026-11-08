#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0179486
# DOI: 10.1371/journal.pone.0179486
# Paper: Li Y, Zhao X, Zhang X, Zhang C, Ma H, Jiao M, et al. (2017).
#   Validation study of the safety attitudes questionnaire (SAQ) in public
#   hospitals of Heilongjiang province, China. PLoS ONE 12(6): e0179486.
# Data: PLOS Supporting Information S1 File (journal.pone.0179486.s001,
#   .xlsx; sheet 1 the data, sheet 2 a codebook with the full English item
#   wording). 1,689 hospital staff in 27 public hospitals.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# ONE output table:
#   li_2017_saq  Safety Attitudes Questionnaire, 30 items (t1-t6 teamwork,
#     s1-s7 safety climate, j1-j5 job satisfaction, st1-st4 stress
#     recognition, p1-p4 perceptions of management, w1-w4 working
#     conditions), 1 disagree strongly .. 5 agree strongly. 999 ("missing
#     data and answered not applicable", codebook) dropped. The two items the
#     codebook marks (R), t2 and s5, are as answered: both correlate
#     negatively with their scale-mates and positively with each other.
# Note: 35 rows repeat the previous row's 30 answers exactly (mostly
#   straight 4s or 5s on paper forms, different age/sex); kept.
# Covariates: gender, age, hospital, profession (codebook labels).
# `id` is the deposit's running id 1..1689.
#
# Item text: NOT SHIPPED. Cheap: the codebook sheet carries the English SAQ
#   wording for all 30 items (published instrument; check the register).

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0179486.s001"
RAW = os.environ.get("LI2017_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
PROF = {1: "physician", 2: "nurse", 3: "technician", 4: "administrator", 5: "other"}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_li2017_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name=0)
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
    assert len(df) == 1689 and df["id"].is_unique
    items = list(df.columns[7:])
    assert len(items) == 30 and items[0] == "t1" and items[-1] == "w4"
    df[items] = df[items].astype(float).replace(999, float("nan"))
    x = df[items]
    others_t = x[["t1", "t3", "t4", "t5", "t6"]].mean(axis=1)
    assert x["t2"].corr(others_t) < 0 and x["t2"].corr(x["s5"]) > 0
    df["cov_gender"] = df["gender"].map({1: "male", 2: "female"})
    df["cov_age"] = df["age"]
    df["cov_hospital"] = df["hospital"].str.strip()
    df["cov_profession"] = df["profession"].map(PROF)
    covs = ["cov_gender", "cov_age", "cov_hospital", "cov_profession"]
    save(df, covs, items, "li_2017_saq", [1, 2, 3, 4, 5])


if __name__ == "__main__":
    convert()
