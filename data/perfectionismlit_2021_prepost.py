#!/usr/bin/env python3
# Source: https://eprints.yorksj.ac.uk/id/eprint/16595
# DOI: 10.25421/yorksj.16595141.v1
# Figshare download: https://ndownloader.figshare.com/files/30718352
# License: CC BY 4.0
#
# Dataset: Perfectionism Literacy Lesson Evaluation
# 68 participants, 16 items across 3 scales:
#   PreQ1-PreQ5  : Pre-intervention questionnaire (5 items, Likert 1-5)
#   PostQ1-PostQ5: Post-intervention questionnaire (5 items, Likert 1-5)
#   EQ1-EQ3      : Engagement/experience questionnaire (3 items, Likert 1-5)
#
# Pre and Post measure the same construct at different time points → wave column.
# EQ is a separate construct → separate output file.
#
# Sentinel 999 used for missing in both item and covariate columns.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

DOWNLOAD_URL = "https://ndownloader.figshare.com/files/30718352"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

VALID_RESP_MIN = 1
VALID_RESP_MAX = 5


def download_data():
    r = requests.get(DOWNLOAD_URL, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), encoding="utf-8-sig")


def clean_cov(val, sentinel=999):
    """Replace sentinel with NaN in covariate columns."""
    return val.replace(sentinel, float("nan"))


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = download_data()

    # Rename ID column
    df = df.rename(columns={"ID": "id"})

    # Covariates — replace 999 sentinel with NaN
    df["cov_gender"] = clean_cov(df["Gender"])
    df["cov_age"] = clean_cov(df["Age"])
    df["cov_school_year"] = clean_cov(df["SchoolYear"])
    df = df.drop(columns=["Gender", "Age", "SchoolYear"])

    cov_cols = ["cov_gender", "cov_age", "cov_school_year"]

    # -----------------------------------------------------------------------
    # Scale 1 & 2: Pre- and Post-intervention items → single file with wave
    # PreQ1-PreQ5  → wave=1
    # PostQ1-PostQ5 → wave=2
    # -----------------------------------------------------------------------
    pre_items = ["PreQ1", "PreQ2", "PreQ3", "PreQ4", "PreQ5"]
    post_items = ["PostQ1", "PostQ2", "PostQ3", "PostQ4", "PostQ5"]

    pre_df = df[["id"] + cov_cols + pre_items].copy()
    pre_long = pre_df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=pre_items,
        var_name="item",
        value_name="resp"
    )
    # Strip "Pre" prefix so items match across waves: PreQ1 → Q1
    pre_long["item"] = pre_long["item"].str.replace("^Pre", "", regex=True)
    pre_long["wave"] = 1

    post_df = df[["id"] + cov_cols + post_items].copy()
    post_long = post_df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=post_items,
        var_name="item",
        value_name="resp"
    )
    post_long["item"] = post_long["item"].str.replace("^Post", "", regex=True)
    post_long["wave"] = 2

    prepost = pd.concat([pre_long, post_long], ignore_index=True)

    # Clean responses
    prepost["resp"] = pd.to_numeric(prepost["resp"], errors="coerce")
    prepost = prepost[prepost["resp"].between(VALID_RESP_MIN, VALID_RESP_MAX)]
    prepost = prepost.dropna(subset=["resp"]).reset_index(drop=True)

    # Enforce column order
    prepost = prepost[["id", "item", "resp", "wave"] + cov_cols]
    prepost = prepost.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    out_name_prepost = "perfectionismlit_2021_perfectionism_prepost.csv"
    out_path_prepost = os.path.join(OUT_DIR, out_name_prepost)
    prepost.to_csv(out_path_prepost, index=False)
    print(f"{out_name_prepost}: rows={len(prepost)} ids={prepost['id'].nunique()} "
          f"items={prepost['item'].nunique()} resp={prepost['resp'].min():.0f}-{prepost['resp'].max():.0f} "
          f"waves={sorted(prepost['wave'].unique())}")

    # -----------------------------------------------------------------------
    # Scale 3: Engagement questionnaire (EQ1-EQ3) — separate construct
    # -----------------------------------------------------------------------
    eq_items = ["EQ1", "EQ2", "EQ3"]
    eq_df = df[["id"] + cov_cols + eq_items].copy()
    eq_long = eq_df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=eq_items,
        var_name="item",
        value_name="resp"
    )

    eq_long["resp"] = pd.to_numeric(eq_long["resp"], errors="coerce")
    eq_long = eq_long[eq_long["resp"].between(VALID_RESP_MIN, VALID_RESP_MAX)]
    eq_long = eq_long.dropna(subset=["resp"]).reset_index(drop=True)

    eq_long = eq_long[["id", "item", "resp"] + cov_cols]
    eq_long = eq_long.sort_values(["id", "item"]).reset_index(drop=True)

    out_name_eq = "perfectionismlit_2021_engagement.csv"
    out_path_eq = os.path.join(OUT_DIR, out_name_eq)
    eq_long.to_csv(out_path_eq, index=False)
    print(f"{out_name_eq}: rows={len(eq_long)} ids={eq_long['id'].nunique()} "
          f"items={eq_long['item'].nunique()} resp={eq_long['resp'].min():.0f}-{eq_long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
