#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0318259
# DOI: 10.1371/journal.pone.0318259
# Paper: Zhang W, Wang J, Wu Y, et al. (2025). Development and validation of
#   the nutrition literacy scale for Chinese gout patients. PLOS ONE 20(2):
#   e0318259.
# Data: S1 File (journal.pone.0318259.s001, "Dataset", .xlsx), 526 Chinese
#   adults with gout.
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# ONE output table, zhang_2025_gout_nutrition_literacy: the study-developed
# 26-item scale, keeping the deposit's codes. Five dimensions (paper):
# A1-A4 nutrition belief, B1-B8 nutrition knowledge, C1-C4 nutrition
# information acquisition, D1-D5 information interaction, E1-E5 information
# criticism. resp 1-5: "strongly disagree .. agree very much" or "never ..
# always" depending on the item (the paper names both anchor sets without
# saying which item uses which). Higher = higher literacy. Items C1, C3, C4
# use only codes 1-3 in this sample.
# Covariate: age. Dropped: Gender, Marital status, Way of living, Residence,
#   Education level -- bare integer codes with no codebook in the deposit or
#   the paper's text.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the
#   Chinese wording of the items is not in the deposit.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ZHANG_GOUT_RAW", "journal.pone.0318259.s001.xlsx")
NAME = "zhang_2025_gout_nutrition_literacy"


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (526, 32)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    items = ([f"A{i}" for i in range(1, 5)] + [f"B{i}" for i in range(1, 9)] + [f"C{i}" for i in range(1, 5)]
             + [f"D{i}" for i in range(1, 6)] + [f"E{i}" for i in range(1, 6)])
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Age"]
    cov_cols = ["cov_age"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    dropped = ["Gender", "Marital status", "Way of living", "Residence", "Education level"]
    assert set(df.columns) - {"id", "cov_age"} == set(items) | {"Age"} | set(dropped)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; dropped {dropped}")


if __name__ == "__main__":
    convert()
