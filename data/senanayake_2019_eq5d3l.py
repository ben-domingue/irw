#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0211604
# DOI: 10.1371/journal.pone.0211604
# Paper: Senanayake S, Mahesh PKB, Gunawardena N, Graves N, Kularatna S
#   (2019). Validity and internal consistency of EQ-5D-3L quality of life tool
#   among pre-dialysis patients with chronic kidney disease in Sri Lanka, a
#   lower middle-income country. PLoS ONE 14(6): e0211604.
# Data: PLOS SI S1 Appendix (journal.pone.0211604.s001, .xlsx), 1,036
#   pre-dialysis CKD patients.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, senanayake_2019_eq5d3l: EQ-5D-3L descriptive system, 5
#   items, 1-3 (no / some / extreme problems): mo (mobility), sc (self-care),
#   ua (usual activities), pd (pain), ad (anxiety/depression). Only scale scores are deposited for SF-36/SF-12, CES-D and GHQ-12,
#   so nothing else ships.
# Covariates: age, sex (0 = male: 646 = the paper's 62.4% male),
#   CKD stage category (ckd_cat_new 0-2, as deposited; unlabelled).
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0211604.s001"
RAW = os.environ.get("SENANAYAKE2019_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_senanayake2019_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 1036
    assert (df["sex"] == 0).sum() == 646
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_age"] = df["age_corrected"]
    df["cov_sex"] = df["sex"].map({0: "male", 1: "female"})
    df["cov_ckd_stage_cat"] = df["ckd_cat_new"]
    covs = ["cov_age", "cov_sex", "cov_ckd_stage_cat"]
    items = {"Eq5Dmob": "mo", "Eq5Dselfc": "sc", "Eq5Duact": "ua",
             "Eq5Dpain": "pd", "Eq5Dmood": "ad"}
    sub = df[["id"] + covs + list(items)].rename(columns=items)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= {1, 2, 3}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "senanayake_2019_eq5d3l"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
