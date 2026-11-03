#!/usr/bin/env python3
# Source: https://doi.org/10.3389/fpsyg.2022.898027 (supplementary data on
#   figshare: Data Sheet 2 = 10.3389/fpsyg.2022.898027.s002, Data Sheet 4 =
#   10.3389/fpsyg.2022.898027.s004)
# DOI: 10.3389/fpsyg.2022.898027
# Paper: Claudy MC, Aquino K, Graso M (2022). Artificial intelligence can't be
#   charmed: The effects of impartiality on laypeople's algorithmic
#   preferences. Frontiers in Psychology 13:898027.
# Data: Qualtrics exports of Study 1 (Data Sheet 2, 120 US Prolific workers,
#   2020) and Study 3 (Data Sheet 4, 323 Prolific workers, 2021).
# License: CC BY 4.0 (verified on both figshare records; the article is CC BY).
#
# Found by the automated_finding repos sweep of 2026-11-02 (mode 3), worked
# from leads/repos_leads_2026-11-02.csv the same day (BATCH_LOG.md). Triage
# flagged the exports for IPAddress / RecipientLastName / RecipientFirstName /
# RecipientEmail / LocationLatitude / LocationLongitude columns: every one of
# them is EMPTY below its Qualtrics header row (checked below), as is the
# Prolific ID column, so there is no PII in the files.
#
# TWO output tables:
#   claudy_2022_procedure_judgments  Study 1. Eight sliders, "In your
#     opinion, which decision procedure would ...": Q42_1 give you a better
#     chance of getting the job, Q42_2 be fairer, Q42_3 be more impartial,
#     Q42_4 be more ethical, Q45_6 give you more control over the hiring
#     decision, Q45_7 be more respectful towards you, Q45_8 involve better
#     communication, Q45_9 be more transparent. resp -10 .. +10, where -10 =
#     the human (HR manager) and +10 = the AI, per the paper ("whether they
#     believed that the decision procedure involving the human (-10) or the AI
#     (+10) would be more impartial"). All 120 recruited (the paper's
#     analyses retain 118; its exclusion flag is not in the file). No
#     manipulation in this study.
#   claudy_2022_hiring_criteria_importance  Study 3. Seven "How important
#     were the following criteria for you in choosing your interviewer?"
#     items, Q10.1_1 .. Q10.1_7, 1 not at all important, 2 slightly,
#     3 moderately, 4 very, 5 extremely important. The 5 respondents who
#     failed the embedded attention check (Q10.1_8, "please select extremely
#     important") are dropped, which reproduces the paper's N retained = 318.
#     The randomised high/low-status vignette arm is NOT carried (open
#     multi-arm `treat` question, as for hazell_2022 and cassaday_2023).
# NOT shipped: Study 1's overall choice (one binary item) and Study 2 (Data
#   Sheet 3: four binary human-vs-AI choices, each asked under one of three
#   randomised framings, so no arm-free item set exists); Study 3's three
#   manipulation-check items, two realism items, and the binary interviewer
#   choice. Free-text answers (Study 1 rationale, comments, Study 3 upsides/
#   downsides) are not carried.
# Covariates: gender, age, political affiliation (Study 1); gender, age,
#   race/ethnicity, years of work experience (Study 3). Ages under 18 (one
#   "12" in Study 1, one "10" in Study 3 -- Prolific requires 18+) are set
#   missing.
# `id` is the row index within each study.
#
# Item text: not shipped (the item wording is above and in each column
#   header; not attempted in this batch).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW1 = os.environ.get("CLAUDY_RAW_S1", "Data_Sheet_2.xlsx")
RAW3 = os.environ.get("CLAUDY_RAW_S3", "Data_Sheet_4.xlsx")
PII_COLS = ["IPAddress", "RecipientLastName", "RecipientFirstName", "RecipientEmail", "LocationLatitude",
            "LocationLongitude", "ExternalReference", "ResponseId"]
S1_ITEMS = ["Q42_1", "Q42_2", "Q42_3", "Q42_4", "Q45_6", "Q45_7", "Q45_8", "Q45_9"]
S3_ITEMS = [f"Q10.1_{k}" for k in range(1, 8)]
IMP = {"Not at all important": 1, "Slightly important": 2, "Moderately important": 3, "Very important": 4,
       "Extremely important": 5}


def read(path, prolific):
    d = pd.read_excel(path).iloc[1:].reset_index(drop=True)  # row 0 = Qualtrics question text
    print(f"PII screen {os.path.basename(path)}: {len(PII_COLS) + 1} identifier columns of {len(d.columns)} examined")
    for c in PII_COLS + [prolific]:
        assert d[c].isna().all(), c
    return d


def age(s):
    a = pd.to_numeric(s, errors="coerce")
    return a.where(a >= 18)


def finish(long, items, permitted, name):
    long = long.dropna(subset=["resp"])
    assert set(long["resp"]) <= set(permitted), set(long["resp"]) - set(permitted)
    long["resp"] = long["resp"].astype(int)
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: list(permitted) for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
    return long


def convert():
    out = {}
    d1 = read(RAW1, "Q149")
    assert len(d1) == 120
    d1["id"] = range(1, len(d1) + 1)
    d1["cov_gender"] = d1["Q74"].str.lower()
    d1["cov_age"] = age(d1["Q75"])
    d1["cov_political_affiliation"] = d1["Q76"]
    c1 = ["cov_gender", "cov_age", "cov_political_affiliation"]
    for c in S1_ITEMS:
        d1[c] = pd.to_numeric(d1[c], errors="raise")
    long = d1[["id"] + c1 + S1_ITEMS].melt(id_vars=["id"] + c1, var_name="item", value_name="resp")
    out["claudy_2022_procedure_judgments"] = finish(long[["id", "item", "resp"] + c1], S1_ITEMS,
                                                    range(-10, 11), "s1")

    d3 = read(RAW3, "Q13.1")
    assert len(d3) == 323
    d3 = d3[d3["Q10.1_8"] == "Extremely important"].reset_index(drop=True)
    assert len(d3) == 318
    d3["id"] = range(1, len(d3) + 1)
    d3["cov_gender"] = d3["Q2.1"].str.lower()
    d3["cov_age"] = age(d3["Q2.2"])
    d3["cov_race_ethnicity"] = d3["Q2.3"]
    d3["cov_work_experience"] = d3["Q12.1"]
    c3 = ["cov_gender", "cov_age", "cov_race_ethnicity", "cov_work_experience"]
    for c in S3_ITEMS:
        d3[c] = d3[c].map(IMP)
    long = d3[["id"] + c3 + S3_ITEMS].melt(id_vars=["id"] + c3, var_name="item", value_name="resp")
    out["claudy_2022_hiring_criteria_importance"] = finish(long[["id", "item", "resp"] + c3], S3_ITEMS,
                                                           range(1, 6), "s3")
    assert len(out) == 2
    os.makedirs(OUT_DIR, exist_ok=True)
    for t, long in out.items():
        long.to_csv(os.path.join(OUT_DIR, f"{t}.csv"), index=False)
        print(f"{t}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
