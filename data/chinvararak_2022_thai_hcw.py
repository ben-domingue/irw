#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268704
# DOI: 10.1371/journal.pone.0268704
# Paper: Chinvararak C, Kerdcharoen N, Pruttithavorn W, Polruamngern N,
#   Asawaroekwisoot T, Munsukpol W, et al. (2022). Mental health among
#   healthcare workers during COVID-19 pandemic in Thailand. PLoS ONE 17(5):
#   e0268704.
# Data: PLOS Supporting Information S1 Data (journal.pone.0268704.s001, Stata
#   .dta). 986 healthcare workers at a Bangkok university hospital, 2021.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# THREE output tables:
#   chinvararak_2022_mbi_gs  Thai MBI-General Survey, 16 items 0-6:
#     mbigs1-5 emotional exhaustion, 6-10 depersonalisation, 11-16 personal
#     accomplishment (positively worded and scored as such, per the paper's
#     cut-points: PA >= 30 is low burnout). As answered: each subscale sum
#     equals the deposit's subscale score on every row (asserted).
#   chinvararak_2022_gad7    GAD-7, 0-3; sum = gad7scr on every row (asserted).
#   chinvararak_2022_phq9    Thai PHQ-9, 0-3. Two-step design: only the 403
#     respondents who screened positive on the 2Q were asked the PHQ-9 (the
#     paper's Methods); sum = phq9scr on every complete row (asserted).
# Dropped: PTSD (3 yes/no criteria, thin), 2Q (2 items), PPE and support
#   single items, Thai free text (occupation, underlying and mental health
#   conditions), derived categories.
# Covariates: sex, age.
# `id` is the deposit's running ID 1..986.
#
# Item text: NOT SHIPPED. MBI-GS, GAD-7 and PHQ-9 are published instruments.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0268704.s001"
RAW = os.environ.get("CHINVARARAK2022_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_chinvararak2022_tmp.dta")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_dta(path)
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
    assert len(df) == 986 and df["id"].is_unique
    df["id"] = df["id"].astype(int)
    df["cov_sex"] = df["sex"].map({0: "male", 1: "female"})
    assert df["cov_sex"].notna().all() and (df["cov_sex"] == "female").sum() == 879
    df["cov_age"] = df["age"]
    covs = ["cov_sex", "cov_age"]

    for a, b, s in [(1, 5, "mbigs1_5scr"), (6, 10, "mbigs6_10scr"), (11, 16, "mbigs11_16scr")]:
        cols = [f"mbigs{i}" for i in range(a, b + 1)]
        assert (df[cols].sum(axis=1) == df[s]).all()
    save(df, covs, [f"mbigs{i}" for i in range(1, 17)], "chinvararak_2022_mbi_gs", range(0, 7))

    gad = [f"gad7_{i}" for i in range(1, 8)]
    assert (df[gad].sum(axis=1) == df["gad7scr"]).all()
    save(df, covs, gad, "chinvararak_2022_gad7", [0, 1, 2, 3])

    phq = [f"phq9_{i}" for i in range(1, 10)]
    full = df[phq].notna().all(axis=1)
    assert full.sum() == 403
    assert (df.loc[full, phq].sum(axis=1) == df.loc[full, "phq9scr"]).all()
    save(df, covs, phq, "chinvararak_2022_phq9", [0, 1, 2, 3])


if __name__ == "__main__":
    convert()
