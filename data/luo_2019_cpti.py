#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0219136
# DOI: 10.1371/journal.pone.0219136
# Paper: Luo J, Wang MC, Wang Y, Zhang X, Deng J, Zhong C, Gao Y, Qi S
#   (2019). Longitudinal measurement invariance of the Child Problematic
#   Trait Inventory in older Chinese children. PLoS ONE 14(7): e0219136.
# Data: PLOS SI S1 (journal.pone.0219136.s001, .xls "585 CPTI for plosone"),
#   585 children at a Guangdong primary school, rated by their mothers on the
#   Chinese CPTI in October 2016 (T1) and a year later (T2).
# License: CC BY 4.0 (the article and its SI).
# Codebook: none deposited; scale from the paper's Measures.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# ONE output table:
#   luo_2019_cpti  Child Problematic Traits Inventory, mother-rated, 28 items
#     (CPTI1..CPTI28) x 2 waves (`wave` 1 = T1, 2 = T2), 1 does not apply at
#     all .. 4 applies very well. `id` = the child (row index); the mother is
#     the informant. 999 (missing) dropped.
# Covariates: grade (3-6, as deposited). Sex dropped: coded 1/2 (292/293)
#   with no codebook and the paper says only "50% girls". Family and income
#   codes unlabelled (999 missing), dropped.
#
# Item text: NOT SHIPPED. No wording deposited; the CPTI is Colins et al.'s.

import os
import re
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0219136.s001"
RAW = os.environ.get("LUO2019_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_luo2019_tmp.xls")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 585
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_grade"] = df["grade"]
    items = [c for c in df.columns if re.fullmatch(r"CPTI\d+_T[12]", c)]
    assert len(items) == 56
    long = df[["id", "cov_grade"] + items].melt(id_vars=["id", "cov_grade"], var_name="src", value_name="resp")
    long["item"] = long["src"].str.extract(r"^(CPTI\d+)_", expand=False)
    long["wave"] = long["src"].str[-1].astype(int)
    long = long[long["resp"].isin([1, 2, 3, 4])].copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "cov_grade"]].sort_values(["id", "wave", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "luo_2019_cpti.csv"), index=False)
    print(f"luo_2019_cpti: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
