#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243357
# DOI: 10.1371/journal.pone.0243357
# Paper: Wondie Y, Mehnert A, Hinz A (2020). The Hospital Anxiety and
#   Depression Scale (HADS) applied to Ethiopian cancer patients. PLOS ONE
#   15(12): e0243357.
# Data: S1 Data "HADS items" (journal.pone.0243357.s001, .sav), 256 adult
#   cancer patients at the University of Gondar hospital, Ethiopia;
#   administered in Amharic.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table:
#   wondie_2020_hads  HADS, H01..H14, each scored 0-3 (paper: "four response
#     options, which are scored with values ranging from 0 to 3"), in SCORED
#     direction -- the odd items sum to the deposit's HADS_Anxiety and the
#     even items to HADS_Depression on every row (checked below).
# Composites HADS_Anxiety, HADS_Depression, HADS_Sum not shipped.
# Covariates: age; sex (variable label "1=Males 2=Females"); patient status
#   (value labels: new admission / follow-up); surgery, chemotherapy and
#   radiotherapy received (0/1). Dropped, because their codes have no labels
#   in the file or the paper: A03 marital status, A04 education, A05
#   religion, A06 children under 18, Tumor (33 site codes), Tumorstage.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Only H01 carries a variable label ("HADS Item 1");
#   no value labels; the Amharic HADS wording is not in the deposit. HADS is
#   a commercial instrument (GL Assessment).

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("WONDIE_RAW", "journal.pone.0243357.s001.sav")
ITEMS = [f"H{i:02d}" for i in range(1, 15)]
DROPPED = {"A03", "A04", "A05", "A06", "Tumor", "Tumorstage", "HADS_Anxiety", "HADS_Depression", "HADS_Sum"}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (256, 29), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert meta.column_names_to_labels["Sex"] == "1=Males  2=Females"
    assert (df[ITEMS[0::2]].sum(axis=1) - df["HADS_Anxiety"]).abs().max() == 0
    assert (df[ITEMS[1::2]].sum(axis=1) - df["HADS_Depression"]).abs().max() == 0
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Age"]
    df["cov_sex"] = df["Sex"].map({1: "male", 2: "female"})
    df["cov_patient_status"] = df["Patientstatus"].map(meta.variable_value_labels["Patientstatus"])
    for c in ["Surgery", "Chemotherapy", "Radiotherapy"]:
        df[f"cov_{c.lower()}"] = df[c].astype("Int64")
    covs = ["cov_age", "cov_sex", "cov_patient_status", "cov_surgery", "cov_chemotherapy", "cov_radiotherapy"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert set(long["resp"]) <= {0, 1, 2, 3}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    used = set(ITEMS) | DROPPED | {"Age", "Sex", "Patientstatus", "Surgery", "Chemotherapy", "Radiotherapy"}
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "wondie_2020_hads.csv"), index=False)
    print(f"wondie_2020_hads: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
