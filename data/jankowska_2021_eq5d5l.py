#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0257998
# DOI: 10.1371/journal.pone.0257998
# Paper: Jankowska A, Golicki D (2021). EQ-5D-5L-based quality of life
#   normative data for patients with self-reported diabetes in Poland.
#   PLoS ONE 16(9): e0257998.
# Data: PLOS SI S1 File (journal.pone.0257998.s004, .xlsx, sheet "dataset"),
#   2,973 respondents of a representative sample of the general Polish adult
#   population (with and without self-reported diabetes).
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, jankowska_2021_eq5d5l: EQ-5D-5L descriptive system, 5
#   items, 1-5 (no problems .. extreme problems / unable to): mo (mobility),
#   sc (self-care), ua (usual activities), pd (pain/discomfort), ad
#   (anxiety/depression). EQ VAS, index and health-state codes dropped.
# Covariates: age, sex, place of residence, education level, diabetes
#   treatment (incl. "No diabetes"), smoking, all as deposited (text labels).
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0257998.s004"
RAW = os.environ.get("JANKOWSKA2021_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_jankowska2021_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name="dataset")
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 2973
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    ren = {"Age": "cov_age", "Sex": "cov_sex", "Place of residence": "cov_residence",
           "Education level": "cov_education", "Diabetes, treatment": "cov_diabetes_treatment",
           "Smoking": "cov_smoking"}
    df = df.rename(columns=ren)
    df["cov_residence"] = df["cov_residence"].str.split().str.join(" ")
    covs = list(ren.values())
    items = {f"5L_{k}": k.lower() for k in ["MO", "SC", "UA", "PD", "AD"]}
    sub = df[["id"] + covs + list(items)].rename(columns=items)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(range(1, 6))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(range(1, 6)))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "jankowska_2021_eq5d5l"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
