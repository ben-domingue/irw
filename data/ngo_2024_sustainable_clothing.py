#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0315502
# DOI: 10.1371/journal.pone.0315502
# Paper: Ngo TTA, Vo CH, Tran NL, Nguyen KV, Tran TD, Trinh YN (2024).
#   Factors influencing Generation Z's intention to purchase sustainable
#   clothing products in Vietnam. PLoS ONE 19(12): e0315502.
# Data: PLOS SI S2 File (journal.pone.0315502.s002, .xlsx, sheet DATA), 641
#   Vietnamese Generation Z consumers; S1 File is the questionnaire.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TEN output tables, one per construct, five-point Likert 1 = strongly
#   disagree .. 5 = strongly agree, items as answered (codes = deposit's):
#   ngo_2024_green_perceived_value (GPV1-4), _green_perceived_quality
#   (GPQ1-5), _perceived_price (PP1-4), _social_influence (SI1-4),
#   _product_design (PD1-3), _environmental_concern (EC1-4),
#   _environmental_knowledge (EK1-3), _environmental_attitude (EAT1-5),
#   _product_attitude (PAT1-4), _purchase_intention (PI1-4).
#   Screened: within-block mean r 0.49-0.57 vs between-block 0.17-0.21; no
#   duplicate rows.
# Covariates: gender (1 = male: 223, 2 = female: 418, as in Table 1),
#   income band (1-5) and purchase frequency (1-3) as deposited.
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0315502.s002"
RAW = os.environ.get("NGO2024_RAW")

BLOCKS = [("GPV", 4, "green_perceived_value"), ("GPQ", 5, "green_perceived_quality"),
          ("PP", 4, "perceived_price"), ("SI", 4, "social_influence"),
          ("PD", 3, "product_design"), ("EC", 4, "environmental_concern"),
          ("EK", 3, "environmental_knowledge"), ("EAT", 5, "environmental_attitude"),
          ("PAT", 4, "product_attitude"), ("PI", 4, "purchase_intention")]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_ngo2024_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name="DATA")
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 641
    assert (df["Gender"] == 1).sum() == 223
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_income"] = df["Income"]
    df["cov_purchase_frequency"] = df["Purchase frequency"]
    covs = ["cov_gender", "cov_income", "cov_purchase_frequency"]
    for code, n, label in BLOCKS:
        src = [f"{code}{i}" for i in range(1, n + 1)]
        long = df[["id"] + covs + src].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert set(long["resp"]) <= set(range(1, 6))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        checks = run_qc(long, permitted_values=list(range(1, 6)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        os.makedirs(OUT_DIR, exist_ok=True)
        name = f"ngo_2024_{label}"
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
