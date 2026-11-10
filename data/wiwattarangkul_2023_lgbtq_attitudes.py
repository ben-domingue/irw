#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ELRWTI
# DOI: 10.1371/journal.pone.0296039 (paper); data 10.7910/DVN/ELRWTI
# Paper: Wiwattarangkul T, Wainipitapong S (2023). Attitudes towards LGBTQ+
#   individuals among Thai medical students. PLoS ONE 18(12): e0296039.
# Data: Harvard Dataverse ELRWTI, Data.xlsx (sheet Attitude_corrected), 806
#   Chulalongkorn medical students, 2021 academic year.
# License: CC0 1.0 (Dataverse record).
# Codebook: none deposited; item wording and keying from the paper's Table 2
#   and Methods.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# TWO output tables:
#   wiwattarangkul_2023_lgbtq_attitude  Thai Attitude towards LGBTQ+
#     questionnaire, Atti_1..Atti_12, 1-5, AS SCORED: the seven negatively
#     worded items (1, 2, 6, 7, 8, 9, 10 per Table 2's "**") are deposited
#     reverse-rated, as the paper scores them. Every item mean matches Table 2
#     (e.g. item 1 "Being LGBTQ+ is a disorder" 4.4) and the item sum equals
#     Atti_sum on every row (mean 42.3, as in the paper).
#   wiwattarangkul_2023_lgbtq_meded  Opinions on LGBTQ+ in medical education,
#     5 study-written items, 1-10 (compulsory and elective coverage 4.9 / 3.7,
#     dress by gender identity 8.8, as in the paper).
# Dropped: gender_open_1..6 and the other identity/family items (no
#   codebook for their codes), GPA, hometown.
# Covariates: age, study year, sex identity (1 male 425 = the paper's
#   52.7%, 2 female, 4 other).
# `id` = the deposit's No (1..806).
#
# Item text: NOT SHIPPED. English renderings of the 12 attitude items are in
#   Table 2 (image); administered in Thai, not deposited.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://dataverse.harvard.edu/api/access/datafile/7473353"
RAW = os.environ.get("WIWATTARANGKUL2023_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_wiwattarangkul2023_tmp.xlsx")
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
    assert len(df) == 806 and df["No"].is_unique
    df["id"] = df["No"]
    df["cov_age"] = df["Age"]
    df["cov_year"] = df["Year"]
    df["cov_sex_identity"] = df["sex_iden"].map({1: "male", 2: "female", 4: "other"})
    covs = ["cov_age", "cov_year", "cov_sex_identity"]
    att = [f"Atti_{i}" for i in range(1, 13)]
    assert (df[att].sum(axis=1) == df["Atti_sum"]).all()
    assert round(df["Atti_1"].mean(), 1) == 4.4
    save(df, covs, att, "wiwattarangkul_2023_lgbtq_attitude", range(1, 6))
    save(df, covs, ["GD_cur", "GD_extra", "GD_learn", "GD_uniform", "GD_doctor"],
         "wiwattarangkul_2023_lgbtq_meded", range(1, 11))


if __name__ == "__main__":
    convert()
