#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/TYC6RI
# DOI (data): 10.7910/DVN/TYC6RI
# Data: Bialowolski, P. (2026). Replication data for "Which Character Strengths
#   Matter for Financial Literacy? Evidence from a Large VIA Survey Sample".
#   Harvard Dataverse. File "for_replication.tab" (original Stata .dta),
#   19,780 VIA Survey respondents. No article is linked from the deposit
#   (checked 2026-11-07).
# License: CC0 1.0, verified on the deposit (Dataverse API, latestVersion.license).
#
# Found by the repos sweep of 2026-11-07 (Step 2b recoverable_format).
# Not the same data as bialowolski_2024_financial_literacy (4,389 Polish
#   adults, 18 items, 10.7910/DVN/MTQGSF).
#
# ONE output table:
#   bialowolski_2026_financial_literacy  flit1..flit8, an 8-item financial
#     literacy quiz scored 0/1. 1 = correct: on all 6,031 rows with every item
#     answered, the item sum equals the deposit's own fin_literacy total.
# "Don't know": the deposit carries two versions of each item. flitN leaves a
#   don't-know answer missing; flitdkN scores it 0 (2,243 such answers on item
#   1). Per datastandard.md, don't know is a non-response, not a wrong answer,
#   so `resp` comes from flitN and those answers are dropped.
# The file is a Stata mi wide set: _1_* .. _10_* are the ten imputations and
#   are NOT used. flitN, without a prefix, is the observed data (m = 0).
# Covariates (Stata value labels): age group, gender, education, country
#   (the deposit pools small-n countries as "Small country"), employment
#   status, marital status, household income, number of children under 18,
#   homeless, veteran.
# Dropped: the 24 VIA character-strength scale scores (scores, not item
#   responses), the three relationship indicators, occupation and job role
#   (28- and 14-category codes outside the scope of this table), the
#   don't-know variants, the fin_literacy totals, and the imputations.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. The eight question stems are not in the deposit,
#   and no article is linked.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("BIALOWOLSKI_RAW", "for_replication.dta")
ITEMS = [f"flit{i}" for i in range(1, 9)]
COVS = {"age": "cov_age_group", "gender": "cov_gender", "educ": "cov_education", "country": "cov_country",
        "empstat": "cov_employment", "marital": "cov_marital", "hhinc": "cov_household_income",
        "kids": "cov_children_under18", "homeless": "cov_homeless", "veteran": "cov_veteran"}


def convert():
    df, meta = pyreadstat.read_dta(RAW)
    assert df.shape == (19780, 270), df.shape
    full = df[ITEMS].notna().all(axis=1)
    assert (df.loc[full, ITEMS].sum(axis=1) == df.loc[full, "fin_literacy"]).all()
    df["id"] = range(1, len(df) + 1)
    for src, dst in COVS.items():
        labels = meta.value_labels[meta.variable_to_label[src]]
        assert set(df[src].dropna().unique()) <= set(labels), src
        df[dst] = df[src].map(labels)
    covs = list(COVS.values())
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1}, set(long["resp"])
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    name = "bialowolski_2026_financial_literacy"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
