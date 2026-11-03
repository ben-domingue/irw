#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248275
# DOI: 10.1371/journal.pone.0248275
# Paper: Almuqrin A, Mutambik I (2021). The explanatory power of social
#   cognitive theory in determining knowledge sharing among Saudi faculty.
#   PLOS ONE 16(3): e0248275.
# Data: S1 Data (journal.pone.0248275.s001), 411 faculty members at Saudi
#   higher-education institutions.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# SEVEN output tables, one per construct of the paper's measurement model,
# every item on 1 strongly disagree .. 5 strongly agree ("all items were
# measured on a Likert-item basis ranging from 1 = Strongly Disagree and 5 =
# Strongly Agree"):
#   almuqrin_2021_ks_personal_outcome   POE_1..7  personal outcome expectations
#   almuqrin_2021_ks_community_outcome  COE_1..5  community outcome expectations
#   almuqrin_2021_ks_self_efficacy      Slf_EF_1..7 knowledge-sharing self-efficacy
#   almuqrin_2021_ks_reputation         REP_1..4
#   almuqrin_2021_ks_altruism           ALT_1..4
#   almuqrin_2021_ks_donation           DK_1..5   knowledge donation
#   almuqrin_2021_ks_collection         CK_1..3   knowledge collection
# Covariate: age (years).
# Dropped: Q1_Cons (consent, constant), Q3_gender, Q4_Educ, Q5_Major,
#   Q6_1_SM, Q7_Mor_1_SM, Q8_yrs_using -- bare integer codes whose categories
#   appear only in Table 2, an image; gender in particular is 212/199 with no
#   way to tell which code is which.
# `id` is the row index (the sheet has no id column).
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the
#   wording is not in the article or SI (Table 1 lists item counts and sources).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ALMUQRIN_RAW", "journal.pone.0248275.s001.xlsx")
BLOCKS = {
    "personal_outcome": ("POE_", 7),
    "community_outcome": ("COE_", 5),
    "self_efficacy": ("Slf_EF_", 7),
    "reputation": ("REP_", 4),
    "altruism": ("ALT_", 4),
    "donation": ("DK_", 5),
    "collection": ("CK_", 3),
}
DROPPED = ["Q1_Cons", "Q3_gender", "Q4_Educ", "Q5_Major", "Q6_1_SM", "Q7_Mor_1_SM", "Q8_yrs_using"]


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (411, 43), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Q2_age"]
    used = {"Q2_age"} | set(DROPPED)
    names, total = [], 0
    for block, (pfx, k) in BLOCKS.items():
        items = [f"{pfx}{i}" for i in range(1, k + 1)]
        used |= set(items)
        long = df[["id", "cov_age"] + items].melt(id_vars=["id", "cov_age"], var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        long = long[["id", "item", "resp", "cov_age"]]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"almuqrin_2021_ks_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    assert used | {"id", "cov_age"} == set(df.columns), set(df.columns) - used
    print(f"total responses {total}; dropped: {DROPPED}")


if __name__ == "__main__":
    convert()
