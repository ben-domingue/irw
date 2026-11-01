#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133413
# DOI: 10.1371/journal.pone.0133413
# Paper: Roskam, I., Galdiolo, S., Hansenne, M., Massoudi, K., Rossier, J.,
#   Gicquel, L., & Rolland, J.-P. (2015). The psychometric properties of the
#   French version of the Personality Inventory for DSM-5. PLOS ONE 10(7):
#   e0133413.
# Data: journal.pone.0133413.s001 (S1 File, "Dataset", .xls, one sheet).
#   2,532 French-speaking adults: 1,593 from Belgium, 536 from Switzerland,
#   403 from France (psychology undergraduates at Poitiers; the Belgian and
#   Swiss samples were community and student volunteers).
# License: CC BY 4.0 (the article; the data is its own Supporting Information
#   file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# ONE output table, roskam_2015_pid5: the full 220-item PID-5 in its French
# version, p1..p220, each "a 4-point Likert-type scale ranging from 0 (very
# false or often false) to 3 (very true or often true)". Column headers are
# positional (p1..p220) with no wording; the codes ship as the headers, so
# item k is PID-5 item k in the published order -- the only tie between code
# and wording is that order, and the description says so.
#
# The file is complete: 2,532 x 220 with no missing cell. Every value is an
# integer 0-3 (checked per item), so nothing was imputed into the item block.
#
# `id` is the row index (no respondent id in the file).
#
# Covariates: age in years (17-89 -- the paper says 18-85; the file carries a
# 17 and a few above 85, shipped as deposited), sex (1 = men, 2 = women: 25.9%
# men per the paper, which the file reproduces), and country (1 = Belgium,
# 2 = Switzerland, 3 = France -- the three counts match the paper's
# 1,593 / 536 / 403 exactly, which is what pins the code-to-country map).
#
# Item text: NOT SHIPPED. The headers are positional and the deposit carries no
# wording. The PID-5 is the American Psychiatric Association's instrument and
# the register already carries the full 220-item form as `block` (purpose- and
# user-scoped grant, all other rights reserved); the French translation is a
# translation of it and inherits the hold.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ROSKAM_RAW", "S1_File.xls")
N_ROWS = 2532
NAME = "roskam_2015_pid5"


def convert():
    df = pd.read_excel(RAW, engine="xlrd")
    assert df.shape == (N_ROWS, 223), df.shape
    items = [f"p{i}" for i in range(1, 221)]
    assert list(df.columns) == ["Age", "sex", "country"] + items
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt
    assert int(df[items].isna().sum().sum()) == 0
    for c in items:
        assert set(df[c].unique()) <= {0, 1, 2, 3}, (c, df[c].unique())
    assert df["country"].value_counts().to_dict() == {1: 1593, 2: 536, 3: 403}
    assert abs((df["sex"] == 1).mean() - 0.259) < 0.002
    print("age:", df["Age"].describe().to_dict())

    df["id"] = range(1, N_ROWS + 1)
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_age": df["Age"].astype(int),
        "cov_sex": df["sex"].map({1: "man", 2: "woman"}),
        "cov_country": df["country"].map({1: "Belgium", 2: "Switzerland", 3: "France"}),
    })
    cov_cols = ["cov_age", "cov_sex", "cov_country"]
    long = df[["id"] + items].melt(id_vars=["id"], value_vars=items, var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)
    long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
    assert long["id"].nunique() == N_ROWS and long["item"].nunique() == 220
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items=220 resp=0-3")


if __name__ == "__main__":
    convert()
