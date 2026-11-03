#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0251733
# DOI: 10.1371/journal.pone.0251733
# Paper: Rodrigues R, Lopez-Caneda E, Almeida-Antunes N, Sampaio A, Crego A
#   (2021). Portuguese validation of the Alcohol Craving Questionnaire-Short
#   Form-Revised. PLOS ONE 16(5): e0251733.
# Data: S1 Data (journal.pone.0251733.s002, .sav), 591 Portuguese university
#   students aged 18-29.
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# ONE output table, rodrigues_2021_acq_sf_r: ACQ1..ACQ12, the Portuguese
# Alcohol Craving Questionnaire-Short Form-Revised (Singleton 1995), 1
# "totally disagree" .. 7 "totally agree". In SCORED direction: the paper
# inverts items 3, 8 and 11, and the deposit's ACQ_Total_PT equals the plain
# mean of the stored items, so those three are already inverted.
# Covariates: sex (value labels), age, and the deposit's AUDIT-based risky-
#   drinker flag (value labels).
# Dropped: ID (a 1..591 row number; `id` is the row index), the factor and
#   total scores ACQ_F1_PT, ACQ_F2_PT, ACQ_F3_PT, ACQ_Total_PT, and the
#   AUDIT_Total and PACS_Total scale totals (no items deposited).
#
# Item text: NOT SHIPPED. No variable or value labels on the items (both
#   levels checked). The Portuguese administration sheet is S1 Appendix
#   (journal.pone.0251733.s001, PDF, stems + endpoint anchors), but the
#   ACQ-SF-R is a third-party instrument (Singleton, Tiffany & Henningfield)
#   with no register grant -- HELD 2026-11-02, register row written.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("RODRIGUES_RAW", "journal.pone.0251733.s002.sav")
NAME = "rodrigues_2021_acq_sf_r"


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (591, 22)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert txt == ["ID"] and list(df["ID"]) == [str(i) for i in range(1, 592)]
    vl = meta.variable_value_labels
    items = [f"ACQ{i}" for i in range(1, 13)]
    assert (df[items].mean(axis=1) - df["ACQ_Total_PT"]).abs().max() < 1e-9
    df["id"] = range(1, len(df) + 1)
    df["cov_sex"] = df["Sex"].map(vl["Sex"])
    df["cov_age"] = df["Age"]
    df["cov_audit_risk"] = df["RISK"].map(vl["RISK"])
    cov_cols = ["cov_sex", "cov_age", "cov_audit_risk"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    assert long["resp"].notna().all() and (long["resp"] % 1 == 0).all()
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
    dropped = ["ID", "ACQ_F1_PT", "ACQ_F2_PT", "ACQ_F3_PT", "ACQ_Total_PT", "AUDIT_Total", "PACS_Total"]
    assert set(meta.column_names) == set(items) | {"Sex", "Age", "RISK"} | set(dropped)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; dropped {dropped}")


if __name__ == "__main__":
    convert()
