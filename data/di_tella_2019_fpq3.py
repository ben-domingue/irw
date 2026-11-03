#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0210757
# DOI: 10.1371/journal.pone.0210757
# Paper: Di Tella M, Ghiggia A, Testa S, Castelli L, Adenzato M (2019). The
#   Fear of Pain Questionnaire: Factor structure, validity and reliability of
#   the Italian translation. PLOS ONE 14(1): e0210757.
# Data: S1 Dataset (journal.pone.0210757.s004, .xlsx, sheet
#   dataset_DiTella_et_al2019), 511 Italian adults from the general
#   population.
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# ONE output table, di_tella_2019_fpq3: FPQ_1..FPQ_30, the Italian Fear of Pain
# Questionnaire-III (McNeil & Rainwater 1998), 1 "not at all" .. 5 "extreme"
# fear. Subscales (deposit totals): minor, severe and medical pain.
# Covariates: age, and current pain intensity (NRS, 0-10).
# Dropped: gender (1/2 with no labels in the deposit), the subscale and total
#   scores, BDI_Totale and STAI_Tot (totals only), and the four *_Retest
#   columns (retest SUBSCALE totals for 164 people; no retest items).
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Column codes only in the data; the Italian
#   translation is S1 File (journal.pone.0210757.s001, docx), but the FPQ-III is
#   a third-party instrument with no register grant -- HELD 2026-11-02,
#   register row written.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("DITELLA_RAW", "journal.pone.0210757.s004.xlsx")
NAME = "di_tella_2019_fpq3"


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (511, 43)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    items = [f"FPQ_{i}" for i in range(1, 31)]
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Age"]
    df["cov_pain_nrs"] = df["NRS"]
    cov_cols = ["cov_age", "cov_pain_nrs"]
    assert (df[items].sum(axis=1) == df["TotalScore_FPQ"]).all()
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
    dropped = ["gender", "MinorPain_FPQ", "SeverePain_FPQ", "MedicalPain_FPQ", "TotalScore_FPQ", "BDI_Totale",
               "STAI_Tot", "MinorPain_FPQ_Retest", "SeverePain_FPQ_Retest", "MedicalPain_FPQ_Retest",
               "TotalScore_FPQ_Retest"]
    assert set(df.columns) - {"id"} - set(cov_cols) == set(items) | {"Age", "NRS"} | set(dropped)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; dropped {dropped}")


if __name__ == "__main__":
    convert()
