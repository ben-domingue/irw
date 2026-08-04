#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0161858
# DOI: 10.1371/journal.pone.0161858
# Supporting Information: journal.pone.0161858_S1_File.xlsx
#
# MnemoCity Task usability/satisfaction survey (children, N=160).
# Raw file mixes usability/satisfaction survey items with derived
# cognitive-task scores (Direct/Inverse CBTT Score, MnemoCity Score) and
# composite Usability/Satisfaction means -- only the raw 1-5 Likert survey
# items are kept as `resp`.
#
# Items kept: US1, US2 (usability, asked after first interaction),
# SA1-SA4 (satisfaction, after first interaction), Q3D (depth-perception
# question, 1-5), Q2_US1, Q2_SA1 (repeated usability/satisfaction items
# asked after both interactions -- distinct items from US1/SA1, kept
# separate rather than as a wave since only these two items repeat).
# Excluded: Direct CBTT Score, Inverse CBTT Score, MnemoCity Score (derived
# cognitive-task scores), Usability, Satisfaction (composite means across
# the above items), PRE1/PRE2 (categorical interaction-preference choice,
# not an ordinal Likert item).

import os
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file?"
          "type=supplementary&id=10.1371/journal.pone.0161858.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["US1", "US2", "SA1", "SA2", "SA3", "SA4", "Q3D", "Q2_US1", "Q2_SA1"]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(pd.io.common.BytesIO(r.content))
    df = df.rename(columns={
        "Code": "id",
        "Age": "cov_age",
        "Gender": "cov_gender",
        "Type of interaction": "cov_interaction_type",
        "Lang": "cov_lang",
    })

    assert df["id"].nunique() == len(df)

    cov_cols = ["cov_age", "cov_gender", "cov_interaction_type", "cov_lang"]

    long = df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_name = "rodriguezandres_2016_mnemocity_usability.csv"
    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
