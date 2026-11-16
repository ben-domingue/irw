#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247664
# DOI: 10.1371/journal.pone.0247664
# Paper: Hart J (2021). Did the COVID-19 pandemic help or hurt Donald Trump's
#   political fortunes? PLoS ONE 16(2): e0247664.
# Data: PLOS SI S1 File (journal.pone.0247664.s001, .sav), 1,763 US adults in
#   six separate cross-sectional survey waves, 23 Mar - 1 Jun 2020.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TWO output tables, items as answered:
#   hart_2021_trump_support  3 items, 1-7 agreement: good job with the
#     economy... (deposit Q7), overall good president (Q8), will vote to
#     re-elect (Q9). The deposited `trumpsupport` is their mean.
#   hart_2021_covid_concern  4 items, 1-5: following coverage (Q3), affected
#     (Q4), time spent thinking (Q5), concern (Q6). `corona` is their mean
#     (asserted).
# `treat` = Pandemic (random assignment; the paper codes priming = 1,
#   control = 0: priming = the pandemic questions came first).
# Covariates: age; survey wave (`day`, 1-6) as cov_survey_wave -- the waves
#   are separate samples, not repeated measures, so it is not `wave`.
#   Gender, political views and party are not carried: the .sav has no value
#   labels for their codes.
# `id` = row index.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0247664.s001"
RAW = os.environ.get("HART2021_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_hart2021_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, mapping, name, values):
    src = list(mapping)
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


def pick(df, prefix):
    out = [c for c in df.columns if c.startswith(prefix)]
    assert len(out) == 1, (prefix, out)
    return out[0]


def convert():
    df = load()
    assert len(df) == 1763
    trump = {pick(df, f"@{k}."): f"trump_{i}" for i, k in enumerate([7, 8, 9], 1)}
    covid = {pick(df, f"@{k}."): f"covid_{i}" for i, k in enumerate([3, 4, 5, 6], 1)}
    assert ((df[list(covid)].mean(axis=1) - df["corona"]).abs() < 1e-6).all()
    assert ((df[list(trump)].mean(axis=1) - df["trumpsupport"]).abs() < 1e-6).all()
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["treat"] = df["Pandemic"].astype(int)
    df["cov_age"] = df[pick(df, "@17.")]
    df["cov_survey_wave"] = df["day"].astype(int)
    covs = ["treat", "cov_age", "cov_survey_wave"]
    save(df, covs, trump, "hart_2021_trump_support", range(1, 8))
    save(df, covs, covid, "hart_2021_covid_concern", range(1, 6))


if __name__ == "__main__":
    convert()
