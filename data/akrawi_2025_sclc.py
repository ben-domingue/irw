#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331115
# S10 File (raw data): https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0331115.s010&type=supplementary
# DOI: 10.1371/journal.pone.0331115
#
# Akrawi N, Rietdijk WJ, Koch BC, van Rosse F, van der Sijs H (2025)
# "The validity and reliability of the Dutch version of the Student
# Satisfaction and Self-Confidence in Learning Scale (SCLC) for pharmacy
# technicians." 13-item scale, 5-point Likert (1=strongly disagree,
# 5=strongly agree), single cross-sectional administration (paper confirms
# no test-retest/repeated-measures design — "only fully completed
# questionnaires" were analyzed, N=129).
#
# The raw file's own "id" column is NOT a reliable person identifier: it
# has 129 rows but only 119 unique values, and the 10 duplicated ids
# correspond to DIFFERENT people (Gender/Age values differ between the two
# rows sharing an id — e.g. id=7 has Gender 1 vs 3), ruling out the
# retriage hypothesis of a resolving wave/timepoint column for genuine
# test-retest data. This is a reused/miscoded id, not a real duplicate
# person. Per datastandard.md's "Missing/unusable person ID" guidance, the
# row index is used as `id` instead, giving 129 unique respondents matching
# the paper's reported N.

import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "journal.pone.0331115_S10_File.xlsx")
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")

ITEM_COLS = [f"ITEM {i}" for i in range(1, 14)]


def convert():
    df = pd.read_excel(RAW, sheet_name="swse final data")
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1  # source `id` column is unreliable (see header note)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("ITEM ", "sclc_", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_name = "akrawi_2025_sclc"
    path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
