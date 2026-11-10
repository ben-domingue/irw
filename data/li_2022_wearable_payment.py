#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0273849
# DOI: 10.1371/journal.pone.0273849
# Paper: Li L, Al Mamun A, Hayat N, Yang Q, Hoque ME, Zainol NR (2022).
#   Predicting the intention to adopt wearable payment devices in China: The
#   use of hybrid SEM-Neural network approach. PLoS ONE 17(8): e0273849.
# Data: PLOS SI S1 Data (journal.pone.0273849.s002, .sav), 403 Chinese adults
#   (20-40). Variable labels carry the bilingual Chinese/English item stems
#   with construct codes (PE-1 ... IA-6); value labels 1-5.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# EIGHT output tables, one per construct, 1-5, items as answered, item codes
#   = the label's construct code (pe_1 ...):
#   li_2022_performance_expectancy (Q9-Q14, 6), _effort_expectancy (Q15-19,
#   5), _social_influence (Q20-24, 5), _facilitating_conditions (Q25-29, 5),
#   _hedonic_motivation (Q30-34, 5), _lifestyle_compatibility (Q35-39, 5),
#   _perceived_trust (Q40-44, 5), _adoption_intention (Q45-50, 6). The
#   deposited construct means equal the item means (asserted for PE..PT).
#   The 5-point value labels read "very dissatisfied .. very satisfied" in
#   Chinese while the stems are agreement statements; the codes are kept.
# Dropped: Q51-Q52 adoption behaviour, Q7-Q8, `Random` (a ~N(50, 3) marker
#   variable), completion time, construct scores.
# Covariates: gender, age band, income band, education, city tier, marital
#   status (Q1-Q6, value labels).
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
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0273849.s002"
RAW = os.environ.get("LI2022_RAW")

BLOCKS = [("pe", 9, 6, "performance_expectancy"), ("ee", 15, 5, "effort_expectancy"),
          ("si", 20, 5, "social_influence"), ("fc", 25, 5, "facilitating_conditions"),
          ("hm", 30, 5, "hedonic_motivation"), ("lc", 35, 5, "lifestyle_compatibility"),
          ("pt", 40, 5, "perceived_trust"), ("ia", 45, 6, "adoption_intention")]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_li2022_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 403
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_gender"] = df["Q1"].map({1: "male", 2: "female"})
    df["cov_age_band"] = df["Q2"].map({1: "20-25", 2: "26-30", 3: "31-35", 4: "36-40"})
    df["cov_income_band"] = df["Q3"]
    df["cov_education"] = df["Q4"]
    df["cov_city_tier"] = df["Q5"]
    df["cov_marital"] = df["Q6"].map({1: "single", 2: "married", 3: "divorced", 4: "widowed"})
    covs = ["cov_gender", "cov_age_band", "cov_income_band", "cov_education", "cov_city_tier", "cov_marital"]
    for code, start, n, label in BLOCKS:
        src = [f"Q{i}" for i in range(start, start + n)]
        if code.upper() in df.columns:
            assert ((df[src].mean(axis=1) - df[code.upper()]).abs() < 1e-6).all(), code
        mapping = {c: f"{code}_{k}" for k, c in enumerate(src, 1)}
        long = df[["id"] + covs + src].rename(columns=mapping).melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert set(long["resp"]) <= set(range(1, 6))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        checks = run_qc(long, permitted_values=list(range(1, 6)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        os.makedirs(OUT_DIR, exist_ok=True)
        name = f"li_2022_{label}"
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
