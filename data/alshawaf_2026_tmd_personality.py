#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0345159
# DOI: 10.1371/journal.pone.0345159
# Paper: Alshawaf HA, Alnemer MA, Alsafwani MA, Alhalal FA, Aljeshi MM,
#   Nazir MA (2026). Temporomandibular disorders among adult patients:
#   Relationship with personality traits and other factors. PLoS ONE 21(3):
#   e0345159.
# Data: PLOS SI S1 File (journal.pone.0345159.s001, old BIFF .xls read with
#   xlrd), 500 adult dental-hospital patients, Dammam, Saudi Arabia.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TWO output tables, items as answered:
#   alshawaf_2026_bfi2s    Big Five Inventory-2 Short Form, 30 items, 1-5, in
#     the deposit's column order (= BFI-2-S order: quiet, softhearted,
#     organised, anxious, art ...); reverse-keyed items as answered. One
#     cell coded 0 (not a scale point) is dropped.
#   alshawaf_2026_fonseca  Fonseca's Anamnestic Index, 10 items scored
#     0 / 5 / 10 (no / sometimes / yes); the deposited TMD total is their
#     sum (asserted). 7 cells holding 1-4 (not a scale point) are dropped.
# Covariates: age, gender (1 = male: 332, 2 = female: 168, as Table 1),
#   nationality (1 Saudi: 465, 2 non-Saudi: 35), education (1-3), income
#   (1-3), arthritis (0/1), all codes as deposited where unlabelled.
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0345159.s001"
RAW = os.environ.get("ALSHAWAF2026_RAW")

FONSECA = ["Diffcultyopening", "moving", "paininchewing", "headache", "Neckpain",
           "Earache", "Noise", "Clenching", "Together", "Nervous"]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_alshawaf2026_tmp.xls")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, engine="xlrd")
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, mapping, name, values):
    src = list(mapping)
    sub = df[["id"] + covs + src].rename(columns=mapping)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].isin(list(values))].copy()
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
    assert len(df) == 500
    assert (df["gender"] == 1).sum() == 332
    assert (df[FONSECA].sum(axis=1) == df["TMD"]).all()
    cols = list(df.columns)
    bfi = cols[cols.index("Quiet"):cols.index("Losscreativity") + 1]
    assert len(bfi) == 30
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_age"] = df["age"]
    df["cov_gender"] = df["gender"].map({1: "male", 2: "female"})
    df["cov_nationality"] = df["nationality"].map({1: "saudi", 2: "non-saudi"})
    df["cov_education"] = df["education"]
    df["cov_income"] = df["income"]
    df["cov_arthritis"] = df["arthratis"]
    covs = ["cov_age", "cov_gender", "cov_nationality", "cov_education", "cov_income", "cov_arthritis"]
    save(df, covs, {c: f"bfi_{k}" for k, c in enumerate(bfi, 1)}, "alshawaf_2026_bfi2s", range(1, 6))
    save(df, covs, {c: f"fonseca_{k}" for k, c in enumerate(FONSECA, 1)}, "alshawaf_2026_fonseca", (0, 5, 10))


if __name__ == "__main__":
    convert()
