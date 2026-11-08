#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0233119
# DOI: 10.1371/journal.pone.0233119
# Paper: Kawakami N, Tran TTT, Watanabe K, Imamura K, Nguyen HT, Sasaki N,
#   et al. (2020). Internal consistency reliability, construct validity, and
#   item response characteristics of the Kessler 6 scale among hospital
#   nurses in Vietnam. PLoS ONE 15(5): e0233119.
# Data: figshare 10.6084/m9.figshare.12005511.v2,
#   Datadepository-ValidationK605.02.19.xlsx. 949 nurses at a Hanoi hospital,
#   2018.
# License: CC BY 4.0 (figshare license field, api.figshare.com/v2/articles/12005511).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# TWO output tables:
#   kawakami_2020_k6      Vietnamese K6, K1-K6, 0 none of the time .. 4 all
#     of the time. N = 949 and mean total 4.57 as in the paper (asserted).
#   kawakami_2020_dass21  DASS-21, 0-3, items named by the deposit's subscale
#     codes (DASSD1-7 depression, DASSA1-7 anxiety, DASSS1-7 stress), in the
#     deposit's (questionnaire) column order.
# Dropped: the JCQ items (22 of the Job Content Questionnaire, 1-4). The
#   deposit does not say whether the negatively worded items (4, 8, 22, 23
#   in the JCQ numbering) were recoded, and the inter-item correlations do
#   not settle it (4 and 8 are near zero, not negative, against the rest of
#   decision latitude), so the table is dropped under the 2026-11-08 rule.
#   EQ-5D-5L (H1-H5, five single-domain items, plus the VAS H6) not shipped.
# Covariates: birth year, sex, marital status, education, from the header
#   codes.
# `id` is the row index (the deposit carries no identifier).
#
# Item text: NOT SHIPPED. K6 and DASS-21 are published instruments.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/22063455"
RAW = os.environ.get("KAWAKAMI2020_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_kawakami2020_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
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
    assert len(df) == 949, df.shape
    c = list(df.columns)
    df["id"] = range(1, len(df) + 1)
    df["cov_birth_year"] = df[c[0]]
    df["cov_sex"] = df[c[1]].map({1: "male", 2: "female"})
    df["cov_marital_status"] = df[c[2]].map({1: "single", 2: "married", 3: "divorced/widowed"})
    df["cov_education"] = df[c[3]].map(
        {1: "vocational school", 2: "college", 3: "university undergraduate", 4: "postgraduate"}
    )
    assert c[1].startswith("Sex (Male=1,Female=2)") and c[3].startswith("Education (Vocation school=1")
    covs = ["cov_birth_year", "cov_sex", "cov_marital_status", "cov_education"]

    k6 = [f"K{i}" for i in range(1, 7)]
    assert round(df[k6].sum(axis=1).mean(), 2) == 4.57
    out = df.rename(columns={k: k.lower() for k in k6})
    save(out, covs, [k.lower() for k in k6], "kawakami_2020_k6", range(0, 5))

    dass = [x for x in c if str(x).startswith("DASS")]
    assert len(dass) == 21
    out = df.rename(columns={x: x.lower() for x in dass})
    save(out, covs, [x.lower() for x in dass], "kawakami_2020_dass21", [0, 1, 2, 3])


if __name__ == "__main__":
    convert()
