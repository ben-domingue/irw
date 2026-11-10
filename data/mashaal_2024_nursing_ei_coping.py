#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0300057
# DOI: 10.1371/journal.pone.0300057
# Paper: Masha'al D, Rababa M, Hayajneh A, Shahrour G (2024). The mediating
#   role of emotional intelligence on nursing students' coping strategies and
#   anxiety during the COVID-19 pandemic. PLoS ONE 19(4): e0300057.
# Data: PLOS SI S1 (journal.pone.0300057.s001, .xls "Minimal data set"), 282
#   Jordanian nursing students, summer semester 2019/2020. Column headers are
#   the full English item stems with spaces removed.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# THREE output tables, items as answered. Item codes are the instrument's own
# item numbers, assigned in column order, which is each instrument's
# published order (checked on the first stems: TEIQue-SF 1 "Expressing my
# emotions with words is not a problem for me", Brief COPE 1 "I've been
# turning to work or other activities...", GAD-7 1 "Feeling nervous, anxious
# or on edge"); the script asserts the first and last header of each block.
#   mashaal_2024_gad7      GAD-7, gad7_1..7, 0-3 (sum = GAD7totalscore).
#   mashaal_2024_teique_sf TEIQue-SF, teique_1..30, 1-7, RAW: the
#     reverse-keyed items are as answered (item 2 correlates -0.18 with item
#     1). The deposited EITotalscore is the plain sum of these raw columns,
#     i.e. it was computed without reverse-keying.
#   mashaal_2024_brief_cope  Brief COPE, cope_1..28, 1-4.
# Dropped: the GAD-7 difficulty item, COVID/background yes-no items (unlabelled
#   1/2 codes), all derived scores and dichotomies.
# Covariates: age (two non-integer ages, 20.5 and 20.6, set missing),
#   gender (1/2: 2 = 209 of 282 = the paper's 74% female), academic year.
# `id` = row index.
#
# Item text: NOT SHIPPED. Headers carry the English stems (spaces stripped);
#   TEIQue-SF, Brief COPE and GAD-7 are third-party (check the register).

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0300057.s001"
RAW = os.environ.get("MASHAAL2024_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_mashaal2024_tmp.xls")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    if not RAW:
        os.remove(path)
    return df


def block(cols, first, n, last_start):
    i = cols.index(first)
    out = cols[i:i + n]
    assert out[-1].startswith(last_start), out[-1]
    return out


def save(df, covs, src, prefix, name, values):
    mapping = {c: f"{prefix}_{k}" for k, c in enumerate(src, 1)}
    sub = df[["id"] + covs + src].rename(columns=mapping)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
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
    assert len(df) == 282
    cols = list(df.columns)
    gad = block(cols, "Feelingnervousanxiousoronedge", 7, "Feelingafraid")
    tei = block(cols, "Expressingmyemotionswithwordsisnotaproblemforme", 30, "Othersadmiremeforbeingrelaxed")
    cope = block(cols, "Ivebeenturningtoworkorotheractivitiestotakemymindoffthings", 28, "Ivebeenmakingfunofthesituation")
    assert (df[gad].sum(axis=1) == df["GAD7totalscore"]).all()
    assert (df[tei].sum(axis=1) == df["EITotalscore"]).all()
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_age"] = df["Age"].where(df["Age"] == df["Age"].round())
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_academic_year"] = df["Academicyear"]
    covs = ["cov_age", "cov_gender", "cov_academic_year"]
    save(df, covs, gad, "gad7", "mashaal_2024_gad7", range(0, 4))
    save(df, covs, tei, "teique", "mashaal_2024_teique_sf", range(1, 8))
    save(df, covs, cope, "cope", "mashaal_2024_brief_cope", range(1, 5))


if __name__ == "__main__":
    convert()
