#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0341457
# S2 Dataset: https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0341457.s002&type=supplementary
# DOI: 10.1371/journal.pone.0341457
#
# Gabriel A, Bitsch V (2026) "Do opinion leaders know more? Knowledge
# accuracy, self-confidence, and media use in agricultural issues."
# Representative German online survey, N=2022. The `id` column checks out
# as unique (2022 unique of 2023 rows; one row has a missing id and is
# dropped) — resolves the retriage "low-confidence id mapping" flag.
#
# Three separate item sets are shipped, matching the Data_Code sheet's
# Variables_Label codebook:
#   1. Knowledge-accuracy items (Q21_SQ001#0..Q21_SQ009#0): 9 true/false
#      agricultural knowledge statements, coded 0=incorrect/1=correct —
#      genuinely binary, NOT Likert (confirmed against codebook: label
#      "True/False").
#   2. Confidence items (Q21_SQ001#1..Q21_SQ009#1): the paired 6-point
#      subjective-probability confidence rating (50%-100% in 10%
#      increments, coded 1-6) for each of the same 9 statements.
#   3. Media-use items (Q24_SQ001-006): 6 media channels, 5-point usage-
#      frequency scale (codebook label "Which media do you use and how
#      intensively...").
# All other Q21_*/Q23_*/Q24_FAC* columns are derived/composite scores
# (accuracy shares, overconfidence indices, opinion-leader classification,
# regression factor scores) per the codebook and are excluded as
# aggregates, not raw item responses. Q23a/d/e are single, conceptually
# distinct single-item measures (not a multi-item scale) and are excluded
# per the no-single-item-scale rule. No imputation is mentioned in the
# paper; validation procedures (implausible completion time / straight-
# lining checks) were used to exclude bad responses, not to impute.

import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "journal.pone.0341457_S2_Dataset.xlsx")
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")

KNOWLEDGE_COLS = [f"Q21_SQ00{i}#0" for i in range(1, 10)]
CONFIDENCE_COLS = [f"Q21_SQ00{i}#1" for i in range(1, 10)]
MEDIA_COLS = [f"Q24_SQ00{i}" for i in range(1, 7)]


def load():
    df = pd.read_excel(RAW, sheet_name="Data_Code")
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column not unique"
    return df


def build_table(df, item_cols, out_name, item_prefix):
    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["item"] = long["item"].str.extract(r"SQ00(\d)")[0].apply(lambda n: f"{item_prefix}_{n}")
    long = long[["id", "item", "resp"]]
    path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = load()
    build_table(df, KNOWLEDGE_COLS, "gabriel_2026_knowledge_correct", "know")
    build_table(df, CONFIDENCE_COLS, "gabriel_2026_knowledge_confidence", "conf")
    build_table(df, MEDIA_COLS, "gabriel_2026_media_use", "media")


if __name__ == "__main__":
    convert()
