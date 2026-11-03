#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0261378
# DOI: 10.1371/journal.pone.0261378
# Paper: Greenhough B, Barrett S, Towlson C, Abt G (2021). Perceptions of
#   professional soccer coaches, support staff and players toward virtual
#   reality and the factors that modify their intention to use it. PLOS ONE
#   16(12): e0261378.
# Data: OSF node t9j4b (public; CC-By Attribution 4.0 International,
#   verified on the node itself via api.osf.io), Rawdata.csv: 207 English
#   professional-football practitioners (143 coaches/support staff, 64
#   players), online survey; one further row is empty.
# Questionnaires: S1 Survey (practitioners) and S2 Survey (players).
# License: CC BY 4.0 (deposit; the article is CC BY 4.0 too).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table, coaches/support staff and players stacked with cov_role
# (both surveys carry the same ten items with the same anchors):
#   greenhough_2021_tri2  Technology Readiness Index 2.0 (Parasuraman &
#     Colby; ten-item form), TRQ1..TRQ10 in S1 Survey's order (optimism 1-2,
#     innovativeness 3-5, discomfort 6-7, insecurity 8-10), 1 strongly
#     disagree, 2 somewhat disagree, 3 neutral, 4 somewhat agree, 5 strongly
#     agree. RAW answers: the discomfort/insecurity items are not reversed
#     (TRQ8-10, "people are too dependent on technology" etc., average about
#     3.8, i.e. agreement).
# NOT shipped: the VR-specific batteries (performance expectancy PE.*, social
#   influence SI.*, the barrier ratings, opinions). They were only partly
#   asked of each role, their anchors are not consistent across blocks, and
#   the paper analyses them as single indicators.
# Covariates: role (coach/support staff vs player), age band, gender and team
#   level (asked of coaches/support staff only; blank for players).
# `id` is the row index.
#
# Item text: NOT SHIPPED. The TRI 2.0 is a licensed instrument
#   (Parasuraman & Colby 2015, (c) A. Parasuraman and Rockbridge Associates);
#   its wording is reproduced in S1/S2 Survey but carries no open terms.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("GREENHOUGH_RAW", "Rawdata.csv")
ITEMS = [f"TRQ{i}" for i in range(1, 11)]


def convert():
    df = pd.read_csv(RAW, encoding="latin1")
    df.columns = [c.replace("ï»¿", "").strip() for c in df.columns]
    assert df.shape == (208, 106), df.shape
    df = df[df["Survey"].notna()].copy()
    assert len(df) == 207
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0
    # every text column is a closed-choice answer: print the widest cardinality
    print("  max distinct values in a text column:", max(df[c].nunique() for c in txt))
    assert max(df[c].nunique() for c in txt) <= 8  # Age: eight bands
    df["id"] = range(1, len(df) + 1)
    df["cov_role"] = df["Survey"].map({"Coach/support staff": "coach or support staff", "Player": "player"})
    df["cov_age_band"] = df["Age"]
    df["cov_gender"] = df["Working.gender"]
    df["cov_team"] = df["team"]
    covs = ["cov_role", "cov_age_band", "cov_gender", "cov_team"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    # books: every other column is a VR-specific battery or empty
    other = [c for c in df.columns if c not in ITEMS + ["Survey", "Age", "Working.gender", "team", "id"] + covs]
    assert all(c.startswith(("KNWL.", "PE.", "SI.", "Access.", "CACE.", "Acc.", "NoAcc.", "No.acc.",
                             "Combine", "Unnamed")) for c in other), other
    print(f"  not shipped: {len(other)} VR-specific / empty columns")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "greenhough_2021_tri2.csv"), index=False)
    print(f"greenhough_2021_tri2: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
