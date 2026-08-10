#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0269609
# DOI: 10.1371/journal.pone.0269609
#
# Butt et al. (2022) "The role of institutional factors and cognitive
# absorption on students' satisfaction and performance in online learning
# during COVID 19." PLOS ONE. License: CC BY 4.0.
#
# S1 File (SAV, N=404) raw survey responses, 7-point Likert (1=Strongly
# Disagree .. 7=Strongly Agree). Six constructs, one file per scale
# (datastandard.md "one scale per file"):
#   - Institutional Factors: IF1,IF2,IF4-IF10,IF12,IF13 (11 items; IF3/IF11
#     absent from raw file -- dropped items, not our omission)
#   - User Satisfaction: US1-US3 (3 items)
#   - Task Technology Fit: TTF1-TTF3 (3 items)
#   - Performance Impact: PI1-PI4,PI6-PI10 (9 items; PI5 dropped -- also
#     present as "PI5_del" aggregate/marker column, excluded)
#   - Cognitive Absorption: CA1,CA2,CA4,CA6 (4 items; CA3/CA5 absent)
#   - Actual Usage: AU1,AU2 (2 items)
# *_Avg columns are subscale aggregate means -- excluded.

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0269609.s003"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "University": "cov_university",
    "Education": "cov_education",
}

SCALES = {
    "butt_2022_institutional_factors": ["IF1", "IF2", "IF4", "IF5", "IF6", "IF7", "IF8", "IF9", "IF10", "IF12", "IF13"],
    "butt_2022_user_satisfaction": ["US1", "US2", "US3"],
    "butt_2022_task_tech_fit": ["TTF1", "TTF2", "TTF3"],
    "butt_2022_performance_impact": ["PI1", "PI2", "PI3", "PI4", "PI6", "PI7", "PI8", "PI9", "PI10"],
    "butt_2022_cognitive_absorption": ["CA1", "CA2", "CA4", "CA6"],
    "butt_2022_actual_usage": ["AU1", "AU2"],
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_butt_2022.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp)
    return df


def convert():
    print("Fetching S1 File (SAV)...")
    raw = fetch_raw()
    df = raw.rename(columns={"ID": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).copy()
    df["id"] = df["id"].astype(int)
    assert df["id"].is_unique, "id column not unique"

    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, item_cols in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        for c in item_cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= 1) & (long["resp"] <= 7)].reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
