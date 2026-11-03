#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0341453
# DOI: 10.1371/journal.pone.0341453
# Paper: Yin H, Amran MS (2026). Psychometric validation and cultural
#   adaptation of executive functioning scale in Malaysian University
#   students. PLOS ONE 21(4): e0341453.
# Data: S1 File (journal.pone.0341453.s001, "Minimal Data Set", .sav), 629
#   Malaysian university students.
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# ONE output table, yin_2026_efs: all 52 administered items of the
# Executive Function Scale (EFS), keeping the deposit's own codes EF1..EF52.
# Items 13 and 35 were dropped from the adapted scale after validation (S2
# File) but were administered and are in the deposit, so they ship. Six
# subscales per
# S2 File: working memory 1-7, 42-46; risk avoidance 8-12, 21, 38; response
# inhibition 29-33, 39-41; emotion regulation 14-20, 22-24; set shifting 34,
# 36, 37, 47-52; processing speed 25-28.
# resp: 1 never .. 5 very often. The S2 File's administration sheet numbers
# the options 0-4; the deposit stores them 1-5, kept as deposited. Items are
# NOT re-keyed (several are negatively worded, e.g. EF44, EF48, EF51).
# Covariate: gender (value labels). Dropped: Q2 major (6 codes, only 4
# labelled, and those as opaque "H1".."S1"), Q3 background ("U"/"P", not
# explained anywhere), and the seven composite columns WM, RA, RI, ER, SS, PS,
# Sum.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. No variable labels on the items and no value labels
#   (both levels checked). The English "localised" item wording is S2 File
#   (journal.pone.0341453.s002), but the administration was in Malay, whose
#   wording is not in the deposit; and the EFS is a third-party instrument
#   (Uljarevic, Thomas et al.) with no register grant -- HELD 2026-11-02,
#   register row written.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("YIN_RAW", "journal.pone.0341453.s001.sav")
NAME = "yin_2026_efs"


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (629, 62)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    items = [f"EF{i}" for i in range(1, 53)]
    assert len(items) == 52 and set(items) <= set(df.columns)
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["Q1"].map(meta.variable_value_labels["Q1"])
    cov_cols = ["cov_gender"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    assert long["resp"].notna().all() and (long["resp"] % 1 == 0).all()
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
    dropped = ["Q2", "Q3", "WM", "RA", "RI", "ER", "SS", "PS", "Sum"]
    assert set(meta.column_names) == set(items) | {"Q1"} | set(dropped)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; dropped {dropped}")


if __name__ == "__main__":
    convert()
