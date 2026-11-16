#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0175883
# DOI: 10.1371/journal.pone.0175883
# Paper: Grandahl M, Larsson M, Tyden T, Stenhammar C (2017). School nurses'
#   attitudes towards and experiences of the Swedish school-based HPV
#   vaccination programme - A repeated cross sectional study. PLoS ONE 12(4):
#   e0175883.
# Data: PLOS SI S2 File "Data set 2016" (journal.pone.0175883.s002, an old
#   BIFF .xls read with xlrd). It stacks both survey rounds: Group 1 = 2013
#   (851 nurses), Group 2 = 2016 (736), matching Table 1.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, grandahl_2017_hpv_attitudes: the 13 attitude statements
#   of question 11 (Table 2), four-point scale 1 = strongly agree,
#   2 = partially agree, 3 = partially disagree, 4 = strongly disagree, as
#   answered (no reverse-keying). Item codes q11_a..q11_m (a serious side
#   effects, b cervical cancer risk if unvaccinated, c complete protection,
#   d offer to boys, e small risk for boys, f painful, g fear of needles,
#   h offer several times, i confidence in the government decision, j less
#   condom use, k more partners, l more STI knowledge, m less Pap-smear
#   participation). Check: 2016 nurses strongly agreeing boys should be
#   offered the vaccine = 415 (the abstract's n = 415), asserted.
#   Codes 99 / 999 (no answer) and 0 (not a scale point) are dropped.
# Covariates: survey year (2013 / 2016). Gender (97% women), birth year,
#   municipality, years as nurse and the free-text comment fields are not
#   carried.
# `id` = row index; the two rounds are independent cross-sections.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0175883.s002"
RAW = os.environ.get("GRANDAHL2017_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_grandahl2017_tmp.xls")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, engine="xlrd")
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 1587
    assert ((df["Group"] == 2) & (df["Q11_d_Boys"] == 1)).sum() == 415
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_survey_year"] = df["Group"].map({1: 2013, 2: 2016})
    covs = ["cov_survey_year"]
    src = [c for c in df.columns if c.startswith("Q11_")]
    assert len(src) == 13
    items = {c: "q11_" + c.split("_")[1] for c in src}
    sub = df[["id"] + covs + src].rename(columns=items)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].isin([1, 2, 3, 4])].copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "grandahl_2017_hpv_attitudes"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
