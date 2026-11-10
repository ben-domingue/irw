#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0272871
# DOI: 10.1371/journal.pone.0272871
# Paper: Lara L, Saracostti M, de-Toro X (2022). Adaptation and psychometric
#   properties of the school engagement and contextual factors questionnaires
#   for Covid-19 and post Covid-19 context. PLoS ONE 17(9): e0272871.
# Data: PLOS SI S2 (journal.pone.0272871.s002, .sav), 913 Chilean
#   municipal-school pupils: 334 in grades 5-6 and 579 in grades 7-8
#   (`Grupo`), each group answering its own grade version.
# License: CC BY 4.0 (the article and its SI).
# Codebook: the .sav variable labels (each column's label is the Spanish
#   item, numbered); S1 File prints both grade versions side by side.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# The two grade versions share item numbers but are worded differently
# (S1 File), so each version is its own table -- FOUR output tables, 1 (never
# or almost never) .. 5 (always or almost always), items as answered:
#   lara_2022_sce_g56 / lara_2022_sce_g78  School Engagement Questionnaire,
#     29 items (affective 10, cognitive 12, behavioural 7; behavioural items
#     3, 4, 9, 11, 23, 28 are misconduct items, not recoded).
#   lara_2022_cfq_g56 / lara_2022_cfq_g78  Contextual Factors Questionnaire,
#     18 items (family 30-32, teachers 33-40, peers 41-47).
# Item codes: `q<n>` from the questionnaire number that opens every column
#   name and label ("@1.Sientoque..." -> q1).
# No covariates are deposited other than the grade group.
# `id` = row index over the whole file.
#
# Item text: NOT SHIPPED. Cheap: the .sav labels carry the grade 5-6
#   wording for all 47 items (the deposit uses those labels for both groups)
#   and S1 File prints both versions; study-authored instruments (Lara,
#   Saracostti et al.), CC BY. Needs the per-version wording split first.

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0272871.s002"
RAW = os.environ.get("LARA2022_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_lara2022_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


def save(df, items, name):
    long = df[["id"] + items].melt(id_vars=["id"], var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4, 5])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert len(df) == 913
    ren = {}
    for c in df.columns[1:]:
        m = re.match(r"@(\d+)\.", c)
        assert m, c
        ren[c] = f"q{int(m.group(1))}"
    assert len(set(ren.values())) == 47
    df = df.rename(columns=ren).reset_index(drop=True)
    df["id"] = df.index + 1
    sce = [f"q{i}" for i in range(1, 30)]
    cfq = [f"q{i}" for i in range(30, 48)]
    assert (df["Grupo"] == 1).sum() == 334 and (df["Grupo"] == 2).sum() == 579
    for g, tag in [(1, "g56"), (2, "g78")]:
        sub = df[df["Grupo"] == g]
        save(sub, sce, f"lara_2022_sce_{tag}")
        save(sub, cfq, f"lara_2022_cfq_{tag}")


if __name__ == "__main__":
    convert()
