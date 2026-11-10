#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0356881
# DOI: 10.1371/journal.pone.0356881
# Paper: Yoshida T, Wakashima K, Takagi G, Sakuraba M, Jordan SS, Sakamoto K,
#   Haruyama R (2026). Associations of solution building and resilience with
#   school refusal behavior among elementary school students. PLoS ONE 21(8):
#   e0356881.
# Data: PLOS SI S1 Data (journal.pone.0356881.s001, .xlsx, sheet "S1 Date"),
#   587 Japanese elementary school students, grades 4-6. Row 1 holds scale
#   names, row 2 the item headers.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# THREE output tables, all 5-point, items as answered:
#   yoshida_2026_sbi_c   Solution Building Inventory for Children, sbi_1..14
#     (sum mean 52.71 in Table 1; asserted to 0.05).
#   yoshida_2026_rss     Resilience Skills Scale for Teenage Children, 17
#     items, named by subscale: calm_1..8, psa_1..4 (positive
#     self-awareness), routine_1..3, selfcare_1..2.
#   yoshida_2026_sras_r_ja  Japanese SRAS-R for school-attending children,
#     sras_1..20.
# Covariates: grade (4-6), gender (1 = boy: 280, 2 = girl: 306, 1 missing,
#   matching the abstract).
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0356881.s001"
RAW = os.environ.get("YOSHIDA2026_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_yoshida2026_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, header=1)
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


def convert():
    df = load()
    assert len(df) == 587
    sbi = {f"SBI-C{i}": f"sbi_{i}" for i in range(1, 15)}
    assert abs(df[list(sbi)].sum(axis=1).mean() - 52.71) < 0.05
    rss = {}
    for stem, short, n in [("Calm relations with self and others", "calm", 8),
                           ("Positive Self-Awareness", "psa", 4),
                           ("Routine Behavior", "routine", 3),
                           ("Self-Care", "selfcare", 2)]:
        rss.update({f"{stem}{i}": f"{short}_{i}" for i in range(1, n + 1)})
    sras = {f"SRAS-R-JA{i}": f"sras_{i}" for i in range(1, 21)}
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_grade"] = df["grade"].astype("Int64")
    df["cov_gender"] = df["gender"].map({1: "boy", 2: "girl"})
    covs = ["cov_grade", "cov_gender"]
    save(df, covs, sbi, "yoshida_2026_sbi_c", range(1, 6))
    save(df, covs, rss, "yoshida_2026_rss", range(1, 6))
    save(df, covs, sras, "yoshida_2026_sras_r_ja", range(1, 6))


if __name__ == "__main__":
    convert()
