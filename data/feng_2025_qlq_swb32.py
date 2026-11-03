#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0321790
# DOI: 10.1371/journal.pone.0321790
# Paper: Feng Y, Luo J, Lin T, et al. (2025). Translation and validation of
#   the Chinese version of EORTC QLQ-SWB32 assessing the spiritual wellbeing
#   of women with gynecological cancer. PLOS ONE 20(4): e0321790.
# Data: S1 Appendix "Data" (journal.pone.0321790.s001, .csv), 200 Chinese
#   women with gynecological cancer.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table:
#   feng_2025_qlq_swb32  EORTC QLQ-SWB32, Chinese (Mandarin) version, items
#     Q1..Q32 by their SWB32 item numbers. Q1-Q31 are 1 "not at all" .. 4
#     "very much"; Q32, global spiritual wellbeing, is 1 "very poor" .. 7
#     "excellent" with an extra 0 "cannot reply or don't know", which is a
#     non-response and is dropped here (15 cells). Raw answers: the paper's
#     reverse scoring of the Relationship with Self scale happens at scoring
#     time. Q24-Q26 are blank for 78 women -- the SWB32 routes only
#     respondents with a belief to the Relationship with God items, and the
#     paper reports 61% (122) answering them.
# Covariates: age; religious belief (0 none / 1 yes: 193 = the paper's 96.5%
#   non-religious). Dropped, because their codes have no labels in the file
#   or the paper: ethnic, marriage, education, work, family_income,
#   caregiver, primary_cancer, cancer_stage, residence.
# `id` is the deposit's own ID.
#
# Item text: NOT SHIPPED. The Chinese and English SWB32 specimens are S2/S3
#   Appendix, but the instrument is EORTC's and is released only under a
#   signed user agreement (the paper's own Data Availability statement).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("FENG_RAW", "journal.pone.0321790.s001.csv")
ITEMS = [f"Q{i}" for i in range(1, 33)]
DROPPED = {"ethnic", "marriage", "education", "work", "family_income", "caregiver", "primary_cancer",
           "cancer_stage", "residence"}


def convert():
    df = pd.read_csv(RAW, encoding="utf-8-sig")
    assert df.shape == (200, 44), df.shape
    for c in ["Q24", "Q25", "Q26"]:
        df[c] = pd.to_numeric(df[c].replace(" ", pd.NA))
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined (after blank-to-NA on Q24-26): {txt}")
    assert len(df.columns) > 0 and txt == []
    assert df["religious_belief"].value_counts().to_dict() == {0: 193, 1: 7}
    assert df["ID"].is_unique
    df["id"] = df["ID"]
    df["cov_age"] = df["Age"]
    df["cov_religious_belief"] = df["religious_belief"].map({0: "no", 1: "yes"})
    covs = ["cov_age", "cov_religious_belief"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    dk = ((long["item"] == "Q32") & (long["resp"] == 0)).sum()
    long = long[~((long["item"] == "Q32") & (long["resp"] == 0))].copy()
    print(f"  dropped {dk} Q32 'cannot reply / don't know' (0) cells")
    long["resp"] = long["resp"].astype(int)
    ok = {**{c: [1, 2, 3, 4] for c in ITEMS[:31]}, "Q32": list(range(1, 8))}
    bad = long[[r not in ok[i] for i, r in zip(long["item"], long["resp"])]]
    assert bad.empty, bad
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values=ok)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    used = set(ITEMS) | DROPPED | {"ID", "Age", "religious_belief"}
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "feng_2025_qlq_swb32.csv"), index=False)
    print(f"feng_2025_qlq_swb32: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
