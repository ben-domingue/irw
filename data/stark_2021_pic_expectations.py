#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254644
# DOI: 10.1371/journal.pone.0254644
# Paper: Stark S, Worm L, Kluge M, Roos M, Burggraf L (2021). The patient satisfaction in primary care consultation -- Questionnaire
#   (PiC): An instrument to assess the impact of patient-centred communication
#   on patient satisfaction. PLoS ONE 16(7): e0254644 (2021).
# Data: PLOS SI S3 File (journal.pone.0254644.s003, .sav, 910 rows), with the
#   authors' SPSS syntax in S4/S5 File. Patients with acute low back pain at 14
#   Franconian GP practices, 2018-19.
# License: CC BY 4.0 (the article and its SI).
# Codebook: the .sav variable/value labels; questionnaire in S1 (German) and
#   S2 (unvalidated English) File.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# ONE output table:
#   stark_2021_pic_expectations  PiC module B ("target state": what the
#     patient expects of a GP consultation), 10 items, 1 = strongly disagree
#     .. 4 = strongly agree, as on the questionnaire.
#   The deposit stores module B AFTER the S4 syntax's
#     `Recode x (1=4) (2=3) (3=2) (4=1)`: the stored item sums equal the
#     deposit's satisfaction_should on all 910 rows, and "I should have the
#     opportunity to talk to the GP" has 747 ones and 1 four. So resp = 5 -
#     stored, which restores the questionnaire's (and the value labels') coding.
#     "Don't know" (0) is already blank in the deposit.
# Dropped: module A ("actual state", 11 items). The S4 syntax recodes it with
#   `(1=4) (2=3) (3=2) (2=1)` -- a typo for (4=1) -- so original "strongly
#   disagree" (1) and "strongly agree" (4) were both stored as 4, and the
#   deposit holds only 2/3/4 with mass at 4 and 2 (stored sums equal
#   satisfaction_is on every row). The two extreme answers can't be told
#   apart, so the module is not recoverable. Also dropped: two general
#   satisfaction items and three duration items (under the 3-item floor /
#   different constructs), the free-text remarks, derived indices.
# `treatment` NOT shipped: the paper's Table 5 has 309 control / 571
#   intervention and the text says intervention = treatment 1, but the deposit
#   has 590 zeros and 320 ones, so its coding contradicts the paper.
# `id` = row index (the questionnaire number repeats across practices: 597
#   distinct values on 910 rows). No GP/practice identifier is deposited.
# Covariates: sex (1 female, 2 male; 2 rows coded 0 set missing), year of
#   birth as deposited, insurance (private/statutory; 0 = no answer, missing).
#   Table 5: 519 female of 880; the deposit has 510 female of 868 answering.
#
# Item text: NOT SHIPPED. English wording is in the .sav variable labels and
#   S2 File (unvalidated translation); the administered German is in S1 File.
#   Study-authored instrument (the PiC is this paper's own), CC BY.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0254644.s003"
RAW = os.environ.get("STARK2021_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}

ITEMS = ["talk_should", "equiv_should", "op_should", "underst_should", "comp_should",
         "disc_should", "trust_should", "idea_should", "fear_should", "exp_should"]
IS_ITEMS = ["talk_is", "ser_is", "op_is", "want_is", "underst_is", "comp_is", "disc_is",
            "sat_is", "idea_is", "fear_is", "exp_is"]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_stark2021_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 910
    # the deposit is post-recode: stored sums equal the deposit's own indices
    assert (df[ITEMS].fillna(0).sum(axis=1) == df["satisfaction_should"]).all()
    assert (df[IS_ITEMS].fillna(0).sum(axis=1) == df["satisfaction_is"]).all()
    assert set(pd.unique(df[IS_ITEMS].values.ravel())[~pd.isna(pd.unique(df[IS_ITEMS].values.ravel()))]) <= {2, 3, 4}
    assert (df["talk_should"] == 1).sum() == 747
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_sex"] = df["sex"].map({1: "female", 2: "male"})
    df["cov_birth_year"] = df["y_birth"].astype("Int64")
    df["cov_insurance"] = df["insurance"].map({1: "private", 2: "statutory"})
    covs = ["cov_sex", "cov_birth_year", "cov_insurance"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= {1, 2, 3, 4}
    long["resp"] = (5 - long["resp"]).astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    name = "stark_2021_pic_expectations"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
