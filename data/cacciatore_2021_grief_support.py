#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0252324
# S1 Data: https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0252324.s002&type=supplementary
# DOI: 10.1371/journal.pone.0252324
#
# Cacciatore J, Thieleman K, Fretts R, Jackson LB (2021) "What is good grief
# support? Exploring the actors and actions in social support after
# traumatic grief." Qualtrics export; row 0 of the raw sheet holds the
# question-text header (not data). Three separate item sets are shipped:
#   1. ISEL-12-style interpersonal support items (Q29-Q40), 4-point
#      "Definitely false" -> "Definitely true" scale.
#   2. Crisis-care satisfaction items (Q24_1-9), 5-point satisfaction scale
#      rated across support-source categories (nursing staff, physicians, ...).
#   3. Ongoing-support satisfaction items (Q25_1-9), same 5-point scale
#      across a different set of support sources (counselors, family, ...).
# Both satisfaction blocks use the identical response category set found in
# the raw data: Extremely dissatisfied < Moderately dissatisfied <
# Adequately satisfied < Moderately satisfied < Extremely satisfied.

import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "journal.pone.0252324_S1_Data.xlsx")
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")

ISEL_ITEMS = [f"Q{n}" for n in range(29, 41)]
CRISIS_ITEMS = [f"Q24_{i}" for i in range(1, 10)]
ONGOING_ITEMS = [f"Q25_{i}" for i in range(1, 10)]

ISEL_MAP = {
    "Definitely false": 1,
    "Probably false": 2,
    "Probably true": 3,
    "Definitely true": 4,
}
SAT_MAP = {
    "Extremely dissatisfied": 1,
    "Moderately dissatisfied": 2,
    "Adequately satisfied": 3,
    "Moderately satisfied": 4,
    "Extremely satisfied": 5,
}
GENDER_MAP = {"Female": "female", "Male": "male", "Non binary": "non_binary"}


def load():
    df = pd.read_excel(RAW)
    df = df.iloc[1:].reset_index(drop=True)  # row 0 is Qualtrics question-text header
    df.insert(0, "id", df.index + 1)
    df["cov_gender"] = df["Q2"].map(GENDER_MAP) if "Q2" in df.columns else None
    return df


def build_table(df, item_cols, value_map, out_name):
    long = df.melt(id_vars=["id", "cov_gender"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(float)
    long = long[["id", "item", "resp", "cov_gender"]]
    path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = load()
    build_table(df, ISEL_ITEMS, ISEL_MAP, "cacciatore_2021_isel")
    build_table(df, CRISIS_ITEMS, SAT_MAP, "cacciatore_2021_crisis_care_satisfaction")
    build_table(df, ONGOING_ITEMS, SAT_MAP, "cacciatore_2021_ongoing_satisfaction")


if __name__ == "__main__":
    convert()
