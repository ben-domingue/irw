#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0167982
# DOI: 10.1371/journal.pone.0167982
# Paper: Nunez, D., Arias, V. B., & Campos, S. (2016). The reliability and
#   validity of Liu's Self-Report Questionnaire for Screening Putative
#   Pre-Psychotic States (BQSPS) in adolescents. PLOS ONE 11(12): e0167982.
# Data: journal.pone.0167982.s001 (S1 File, "CFA Data Set", .xlsx, sheet
#   CFA), 684 high-school students aged 12-21 (paper: 727 recruited, aged
#   13-18) from six secondary schools in Talca, Chile, April-July 2014.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, nunez_2016_bqsps: LIU_01-LIU_15, the Spanish adaptation
# of Liu et al.'s 15-item Brief Self-Report Questionnaire for Screening
# Putative Pre-psychotic States, 1 (never) .. 5 (very often), as deposited.
#
# NOT shipped:
#   * S2 File (s002, "SEM Data Set", 669 rows): every one of its rows is
#     a row of the CFA sheet (matched on gender, age and all 15 LIU items),
#     so it adds no respondents. Its extra SUI_01-SUI_05 columns are the
#     Okasha suicidality items, but the paper describes a FOUR-item Okasha
#     scale and the deposit has five columns with no codebook, and the two
#     sheets share no id to join them by -- left out on err-on-exclusion.
#   * The young-adult sample (245) the paper also analyses is not deposited.
#   * CLUSTER 1 (codes 1-5): unlabelled; the paper describes six schools,
#     so it is not a school code and its meaning is unknown.
#   * Gender (0/1, 50.1% coded 1): unlabelled, and the paper's 50.7% women
#     (of 727) cannot tell 0 from 1 at this split. Left out rather than
#     guessed.
# Covariate: age. `id` is the row index (the sheet has no id column).
#
# Item text: NOT SHIPPED. The sheet has codes only; the Spanish adapted
#   items are in S1 Table (journal.pone.0167982.s003, "Adapted items in
#   Spanish", keyed by item number). The BQSPS is a named third-party
#   instrument (Liu et al. 2013) with no grant in the register -- HELD
#   2026-11-02, register row written.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("NUNEZ_RAW", "journal.pone.0167982.s001.xlsx")
NAME = "nunez_2016_bqsps"
N_ROWS = 684


def convert():
    df = pd.read_excel(RAW, sheet_name="CFA")
    df.columns = [c.strip() for c in df.columns]
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 18 and txt == []
    items = [f"LIU_{i:02d}" for i in range(1, 16)]
    df["id"] = range(1, N_ROWS + 1)
    df["cov_age"] = df["Age"]
    long = df[["id", "cov_age"] + items].melt(id_vars=["id", "cov_age"], var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp", "cov_age"]]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    assert set(df.columns) - {"id", "cov_age"} == set(items) | {"CLUSTER 1", "Gender", "Age"}
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; "
          "dropped CLUSTER 1 and Gender (unlabelled)")


if __name__ == "__main__":
    convert()
