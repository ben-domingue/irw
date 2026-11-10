#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.14139944
# DOI: 10.1371/journal.pone.0251984 (paper); data 10.6084/m9.figshare.14139944
# Paper: Gori A, Topino E, Palazzeschi L, Di Fabio A (2021). Which personality
#   traits can mitigate the impact of the pandemic? Assessment of the
#   relationship between personality traits and traumatic events in the
#   COVID-19 pandemic as mediated by defense mechanisms. PLoS ONE 16(5):
#   e0251984.
# Data: figshare 14139944, Database_.sav (no value labels on items); 557
#   Italian adults, Google Forms, 24-31 March 2020.
# License: CC BY 4.0 (stated on the figshare record).
# Codebook: none; scales from the paper's Measures section.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# THREE output tables:
#   gori_2021_iesr   Impact of Event Scale-Revised (Italian), 22 items, 0-4.
#   gori_2021_dsq40  Defense Style Questionnaire-40 (Italian), 40 items, 1-9.
#   gori_2021_tipi   Italian TIPI, 10 items as answered, 1-7. The paper says
#     "0 (disagree strongly) to 7"; the deposit holds 1-7 only and its
#     reversed copies R_ITIPI_k_R equal 8 - x on every row, i.e. a 1-7 scale
#     (the TIPI's own range). The copies are not used.
# MEAN-IMPUTED CELLS DROPPED: every item column carries exactly one
#   non-integer value (e.g. IESR_1 = 1.6871...), a per-column constant close
#   to but not equal to the column mean -- mean substitution, done on a
#   slightly different sample. 37 respondents have such cells (some on every
#   item); those cells are dropped, which removes respondents with nothing
#   else. The paper does not mention imputation.
# Covariates: age, sex (397 women / 160 men, as in the paper).
# `id` = row index.
#
# Item text: NOT SHIPPED. No wording deposited (published instruments).

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/26824751"
RAW = os.environ.get("GORI2021_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_gori2021_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


def save(df, items, name, values):
    covs = ["cov_age", "cov_sex"]
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    frac = long["resp"] != long["resp"].round()
    # one imputed constant per item
    assert (long[frac].groupby("item")["resp"].nunique() == 1).all()
    long = long[~frac].copy()
    assert set(long["resp"]) <= set(values)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} dropped_imputed={int(frac.sum())}")


def convert():
    df = load()
    assert len(df) == 557
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_age"] = df["Age"]
    df["cov_sex"] = df["SEX"].map({1: "male", 2: "female"})
    assert (df["cov_sex"] == "female").sum() == 397
    for k in (2, 6, 8, 9, 10):
        assert ((df[f"R_ITIPI_{k}_R"] + df[f"ITIPI_{k}"]).round(6) == 8).all()
    save(df, [f"IESR_{i}" for i in range(1, 23)], "gori_2021_iesr", range(0, 5))
    save(df, [f"DSQ40_{i}" for i in range(1, 41)], "gori_2021_dsq40", range(1, 10))
    save(df, [f"ITIPI_{i}" for i in range(1, 11)], "gori_2021_tipi", range(1, 8))


if __name__ == "__main__":
    convert()
