#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288110
# DOI: 10.1371/journal.pone.0288110
# Paper: Celik, E., Dombak, K., Kaya, M., Sahranc, U., Makas, S., Kocak, L.,
#   Takunyaci, M., & Bekir, S. (2023). Examining the attitudes of
#   sexually abused and non-abused individuals towards marriage in terms of
#   ambivalent sexism. PLOS ONE 18(7): e0288110.
# Data: journal.pone.0288110.s001 (S1 Dataset, .sav), 718 adults aged 18-48,
#   Turkey.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# TWO output tables:
#   celik_2023_marriage_attitude  Marriage_Attitude1-21: Inonu Marriage
#       Attitude Scale (Turkish), 1-5.
#   celik_2023_asi                Hostile_Sexism1-11 and Protective_Sexism12-22:
#       the Turkish Ambivalent Sexism Inventory (Glick & Fiske 1996; Turkish
#       adaptation), hostile and protective (benevolent) halves, 1-6.
# As deposited; nothing reversed. No value labels on any item (the response
# ranges are the observed ones, 1-5 and 1-6, matching each instrument's
# format). The three *_Total columns are dropped.
#
# Covariates: parents' marital status (married / divorced) and whether the
# respondent reports having been sexually abused (yes / no) -- the study's
# own grouping variable -- both from the .sav's value labels. The deposit
# carries no gender or age column. Neither covariate identifies anyone.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. No variable labels and no value labels on any item
#   (both levels checked); the Turkish wording is not in the article or SI.
#   The ASI is registered `hold` (2026-10-27); the Inonu scale is a named
#   published instrument.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CELIK_RAW", "journal.pone.0288110.s001.sav")
N_ROWS = 718
TABLES = {
    "marriage_attitude": ([f"Marriage_Attitude{i}" for i in range(1, 22)], range(1, 6)),
    "asi": ([f"Hostile_Sexism{i}" for i in range(1, 12)] + [f"Protective_Sexism{i}" for i in range(12, 23)],
            range(1, 7)),
}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 48 and txt == []
    vl = meta.variable_value_labels
    df["id"] = range(1, N_ROWS + 1)
    df["cov_parents_marital_status"] = df["marital_status_of_parents"].map(vl["marital_status_of_parents"])
    df["cov_sexually_abused"] = df["Have_you_been_sexually_abused"].map(vl["Have_you_been_sexually_abused"])
    cov_cols = ["cov_parents_marital_status", "cov_sexually_abused"]
    assert df[cov_cols].notna().all().all()
    names, total = [], 0
    for suffix, (items, scale) in TABLES.items():
        assert all(c not in vl and meta.column_names_to_labels.get(c) is None for c in items)
        long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(scale), (suffix, set(long["resp"]))
        long = long[["id", "item", "resp"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(scale) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {suffix} {c.name}: {c.detail[:160]}")
        name = f"celik_2023_{suffix}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={len(items)}")
    assert len(set(names)) == len(names)
    accounted = {c for items, _ in TABLES.values() for c in items} | {
        "marital_status_of_parents", "Have_you_been_sexually_abused", "Marriage_Attitude_Total",
        "Hostile_Sexism_Total", "Protective_Sexism_Total"}
    assert set(meta.column_names) == accounted
    print(f"total responses {total}; dropped the three *_Total columns")


if __name__ == "__main__":
    convert()
