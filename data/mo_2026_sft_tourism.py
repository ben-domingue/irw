#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0361990
# DOI: 10.1371/journal.pone.0361990
# Paper: Mo H, Wei M, Liu J (2026). Short-video content perceptions,
#   intention, and self-reported behavior in special forces-style tourism:
#   Evidence from Chinese generation Z university students. PLOS ONE 21(11):
#   e0361990.
# Data: figshare 10.6084/m9.figshare.33440560 (Hongjing Mo), two files:
#   SFT_Survey_Anonymized_Data_526.xlsx (526 rows x 39 columns, the item-level
#   survey; used) and SFT_Standardized_Latent_Variable_Scores_fsQCA_526.xlsx
#   (latent scores; not used). Codes for the background variables are written
#   into the column headers. S1 Appendix (DOCX, on the article) lists the 28
#   measurement items and their sources.
# License: CC BY 4.0 (figshare record).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# flag good).
#
# SEVEN output tables, one per construct, 4 items each, "All construct items
# used a five-point Likert scale" (paper, 3.2). Item codes are the deposit's
# headers.
#   ATT    attitude toward SFT                   -> mo_2026_sft_attitude
#   INT    intention to engage in SFT            -> mo_2026_sft_intention
#   BEH    self-reported SFT-related behavior    -> mo_2026_sft_behavior
#   PCA    perceived content appeal              -> mo_2026_sft_content_appeal
#   PCT    perceived content trustworthiness     -> mo_2026_sft_content_trust
#   PBC    perceived behavioral control          -> mo_2026_sft_pbc
#   SVPUI  short-video platform usage intensity  -> mo_2026_sft_platform_use
#
# Covariates (codes as in the headers): cov_education (1 = undergraduate,
#   2 = master's, 3 = doctoral, 4 = other), cov_gender (1 = male, 2 = female),
#   cov_major (1 = humanities .. 6 = other), cov_travel_past_year (1 = yes,
#   2 = no), cov_daily_video_use (1 = 0-30 min .. 4 = more than 2 h),
#   cov_posted_travel_video (1 = yes, 2 = no), cov_sft_experience (1 = yes,
#   2 = no but want to, 3 = no and do not want to), cov_monthly_expenses
#   (1 = <1,000 RMB .. 5 = >5,000).
# DROPPED: the two eligibility screeners (current student; has seen SFT
#   short-video content), constant 1 by design (asserted).
# `id`: "Case Number", 1-526, unique (asserted).
#
# Imputation: none; no missing cells; every item cell an integer 1-5 (asserted).
#
# Item text: not shipped -- S1 Appendix holds the 28 items, adapted from cited
#   sources; left for the itemtext pass with its rights question.
#
# PII: none -- every column is a coded screener, demographic or item.

import os
import socket
import sys
import tempfile

import pandas as pd
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/68232088"
RAW = os.environ.get("MO_SFT_RAW", "")
N_ROWS = 526
CONSTRUCTS = {
    "ATT": "mo_2026_sft_attitude",
    "INT": "mo_2026_sft_intention",
    "BEH": "mo_2026_sft_behavior",
    "PCA": "mo_2026_sft_content_appeal",
    "PCT": "mo_2026_sft_content_trust",
    "PBC": "mo_2026_sft_pbc",
    "SVPUI": "mo_2026_sft_platform_use",
}
COV_PREFIX = {
    "Education level": "cov_education",
    "Gender": "cov_gender",
    "Major category": "cov_major",
    "Cross-city/province travel": "cov_travel_past_year",
    "Daily short-video use": "cov_daily_video_use",
    "Posted tourism short videos": "cov_posted_travel_video",
    "SFT experience": "cov_sft_experience",
    "Monthly disposable living expenses": "cov_monthly_expenses",
}
SCREENERS = ("Current university student", "Seen SFT short-video content")


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "sft_survey.xlsx")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def convert():
    df = pd.read_excel(fetch())
    assert df.shape == (N_ROWS, 39), df.shape
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s)")
    assert len(df.columns) > 0 and not strings

    covs = {}
    for c in df.columns:
        for p, new in COV_PREFIX.items():
            if c.startswith(p):
                covs[c] = new
    assert len(covs) == len(COV_PREFIX), covs
    screeners = [c for c in df.columns if c.startswith(SCREENERS)]
    assert len(screeners) == 2 and (df[screeners] == 1).all().all()
    assert df["Case Number"].is_unique
    items_all = [f"{p}{i}" for p in CONSTRUCTS for i in range(1, 5)]
    accounted = set(items_all) | set(covs) | set(screeners) | {"Case Number"}
    assert accounted == set(df.columns), set(df.columns) ^ accounted
    assert int(df.isna().sum().sum()) == 0

    df = df.rename(columns={"Case Number": "id", **covs})
    cov_cols = list(COV_PREFIX.values())
    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, name in CONSTRUCTS.items():
        cols = [f"{prefix}{i}" for i in range(1, 5)]
        assert df[cols].isin(range(1, 6)).all().all(), name
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values=list(range(1, 6)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()}")
    assert len(set(CONSTRUCTS.values())) == len(CONSTRUCTS)
    assert total == 28 * N_ROWS
    print(f"7 tables, {total} responses; dropped the 2 constant screeners; "
          f"all source columns accounted for")


if __name__ == "__main__":
    convert()
