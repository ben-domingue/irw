#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0187954
# DOI: 10.1371/journal.pone.0187954
# Paper: Morote, R., Hjemdal, O., Martinez Uribe, P., & Corveleyn, J. (2017).
#   Psychometric properties of the Resilience Scale for Adults (RSA) and its
#   relationship with life-stress, anxiety and depression in a Hispanic
#   Latin-American community sample. PLOS ONE 12(11): e0187954.
# Data: journal.pone.0187954.s001 (S1 Dataset, .sav), 805 adults from a
#   community sample in Lima, Peru (after the paper's exclusions).
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, morote_2017_rsa: the 33-item Spanish Resilience Scale
# for Adults (Friborg, Hjemdal et al.), semantic-differential format, 1-7.
# Item ids are the deposit's own column names, whose two-letter prefix is
# the subscale: Ps perception of self, Pf planned future, Sc social
# competence, Fc family cohesion, Sr social resources, Ss structured style.
#
# DIRECTION: the deposit holds SCORED items -- the paper reverses 17 of the
# 33, and higher is more resilient on every column here. Checked rather than
# assumed: the mean of the six Fc items equals the deposit's own RSA4_FC
# score on every row, and Fc10i (the "i" marks an inverted item) enters that
# mean unflipped. So the raw semantic-differential pole a respondent marked
# is NOT recoverable from this file for the 17 reversed items.
#
# Covariates: sex, age, education (EducRec: high school / technical /
# undergraduate / postgraduate) and employment (EmpRecod2), all with the
# .sav's value labels. Dropped: place of birth (Lima / region), the other
# education and employment recodes, age at first employment, the life-event
# count (SLETotal), the HSCL-25 means (item-level HSCL data is not in the
# deposit) and all RSA subscale/total/log scores.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. No variable labels on the items and value labels
#   that are just the numbers 1-7 (both levels checked); the Spanish
#   semantic-differential pairs are not in the article or its SI. The RSA is
#   a named published instrument.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("MOROTE_RAW", "journal.pone.0187954.s001.sav")
NAME = "morote_2017_rsa"
N_ROWS = 805


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 62 and txt == []
    items = list(df.columns[11:44])
    assert len(items) == 33 and items[0] == "Ps1" and items[-1] == "Sr33"
    assert all(meta.column_names_to_labels.get(c) is None for c in items)
    fc = [c for c in items if c.startswith("Fc")]
    assert (df[fc].mean(axis=1) - df["RSA4_FC"]).abs().max() < 1e-9
    vl = meta.variable_value_labels
    df["id"] = range(1, N_ROWS + 1)
    df["cov_sex"] = df["Sex"].map(vl["Sex"])
    df["cov_age"] = df["Age"]
    df["cov_education"] = df["EducRec"].map(vl["EducRec"])
    df["cov_employment"] = df["EmpRecod2"].map(vl["EmpRecod2"])
    cov_cols = ["cov_sex", "cov_age", "cov_education", "cov_employment"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == set(range(1, 8))
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    dropped = [c for c in meta.column_names if c not in items and c not in ("Sex", "Age", "EducRec", "EmpRecod2")]
    assert len(dropped) == 62 - 33 - 4
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; dropped {dropped}")


if __name__ == "__main__":
    convert()
