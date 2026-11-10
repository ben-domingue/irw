#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0234240
# DOI: 10.1371/journal.pone.0234240
# Paper: Kubota C, Inada T, Nakamura Y, ... Ozaki N (2020). Validation and
#   factor structure of the Japanese version of the inventory to diagnose
#   depression, lifetime version for pregnant women. PLoS ONE 15(6):
#   e0234240.
# Data: PLOS SI S1 (journal.pone.0234240.s001, .xlsx sheet Rawdata), 558
#   pregnant women at four Nagoya hospitals (the paper analyses 556).
# License: CC BY 4.0 (the article and its SI).
# Codebook: none deposited; scales from the paper's Methods.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# TWO output tables:
#   kubota_2020_iddl  IDDL (Japanese), 22 symptom items W1IDDL<k>_1, 0-4. The
#     "lasted longer than 2 weeks" yes/no follow-ups (_2, asked only when the
#     item is >= 1) and item 23 (1/2) are not carried.
#   kubota_2020_epds  EPDS (Japanese), 10 items, 0-3 as scored (the sum equals
#     W1EPDSTOTAL on every complete row).
# `cluster_id` = hospital (0-3, the deposit's codes; one of the four sites).
# Covariates: age, parity, years of schooling. Employment code (unlabelled),
#   income bands, partner's age, gestational day and the SPSS filter dropped.
# `id` = the deposit's ID.
#
# Item text: NOT SHIPPED. No wording deposited; IDDL (Zimmerman) and EPDS
#   (Cox) are third-party instruments.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0234240.s001"
RAW = os.environ.get("KUBOTA2020_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_kubota2020_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name="Rawdata")
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, items, name, values):
    cols = ["id", "cluster_id"] + covs
    long = df[cols + items].melt(id_vars=cols, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cluster_id"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert len(df) == 558 and df["ID"].is_unique
    df["id"] = df["ID"]
    df["cluster_id"] = df["hospital"]
    df["cov_age"] = df["AGE"]
    df["cov_parity"] = df["parity"]
    df["cov_schooling_years"] = df["schooling"]
    covs = ["cov_age", "cov_parity", "cov_schooling_years"]
    epds = [f"W1EPDS{i}" for i in range(1, 11)]
    full = df[epds].notna().all(axis=1)
    assert (df.loc[full, epds].sum(axis=1) == df.loc[full, "W1EPDSTOTAL"]).all()
    iddl = [f"W1IDDL{i}_1" for i in range(1, 23)]
    save(df, covs, iddl, "kubota_2020_iddl", range(0, 5))
    save(df, covs, epds, "kubota_2020_epds", range(0, 4))


if __name__ == "__main__":
    convert()
