#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0300107
# DOI: 10.1371/journal.pone.0300107
# "A comparative analysis of attitudes toward genome-edited food among
# Japanese public and scientific community" (Shineha et al., 2024).
# General public N=4000, experts N=398 (same questionnaire structure,
# combined in one SI dataset with a Category covariate).
#
# SI file used: S1 Dataset (SAV),
# https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0300107.s002&type=supplementary
# Item wording confirmed against S1 File (questionnaire DOCX),
# https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0300107.s001&type=supplementary
# License: CC BY 4.0 (confirmed on article page).
#
# Three distinct item batteries -> three output tables. The original
# USER_ID is only populated for the public sample (NaN for experts), so a
# fresh row-index id is used across the combined sample instead.
#
# Excluded: Fig2a/b/c (Q11/Q14/Q15) are single "select one statement"
# nominal-choice items (e.g. labeling-policy stance) with an embedded
# "I don't know" / "other" non-response category mixed into the numeric
# range -- not a clean ordinal scale, so dropped per the sentinel-code and
# ordinal-response rules in datastandard.md.

import io
import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file?"
           "id=10.1371/journal.pone.0300107.s002&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Q1, Q3, Q4, Q5: general attitude/awareness items (heterogeneous scale
# widths per item: Fig1a is 1-3, Fig1b-d are 1-7; each item is internally
# ordinal and consistent, which is all datastandard.md requires).
ATTITUDE_COLS = ["Fig1a", "Fig1b", "Fig1c", "Fig1d"]

# Q7: "choose three interesting topics" -> per-topic binary indicator (0/1)
TOPICS_COLS = [f"Fig3_{i}" for i in range(1, 18)]

# Q6: "choose three important factors for social acceptance" -> per-factor
# binary indicator (0/1)
FACTORS_COLS = [f"Fig4_{i}" for i in range(1, 12)]

SCALES = {
    "shineha_2024_gef_attitudes": ATTITUDE_COLS,
    "shineha_2024_gef_info_topics": TOPICS_COLS,
    "shineha_2024_gef_accept_factors": FACTORS_COLS,
}


def load_raw() -> pd.DataFrame:
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = load_raw()

    # USER_ID is NaN for the expert subsample -> use a fresh row index as id
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    df["cov_category"] = df["Category"].map({1.0: "general_public", 2.0: "expert"})
    cov_cols = ["cov_category"]

    os.makedirs(OUT_DIR, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
