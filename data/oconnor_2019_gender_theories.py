#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0218333
# DOI: 10.1371/journal.pone.0218333
# Paper: O'Connor C, Maher P, Kadianaki I (2019). Exploring the relationship
#   between lay theories of gender and attitudes to abortion in the context of
#   a national referendum on abortion policy. PLOS ONE 14(6): e0218333.
# Data: S1 Dataset (journal.pone.0218333.s002, Study 1, 348 rows) and S2 Dataset
#   (.s003, Study 2, 241 rows), Irish adults, online, before the May 2018
#   referendum on the Eighth Amendment. Study materials: S1 Appendix (.s001).
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# ONE output table, oconnor_2019_gender_theories: the 11-item lay theories of
# gender scale (gendertheory_1..11; biological and social theory items), 1
# strongly disagree .. 7 strongly agree, administered identically in both
# studies (S1 Appendix) and merged with cov_study (1, 2) per the
# collapse-same-instrument rule. In each study the scale was answered AFTER a
# randomly assigned YES or NO argument (cond_yes_no) built on a biological
# (Study 1) or social (Study 2) theory of gender; that two-arm assignment is
# NOT included, as with the other randomised manipulations in this backlog.
# The study-level passage difference is what cov_study carries. Only
# respondents with item data are in the table (284 + 182 = 466).
# Covariates: study, gender (labels; "Other" kept), age in years, marital
#   status (labels), religion (labels), political orientation (1-5 as
#   deposited), education (labels).
# Dropped: ResponseID (a Qualtrics response id; replaced by the row index, not
#   hashed), birth_year_cleaned (age in years carries the same information),
#   the vote and argument-rating variables (single questions tied to the
#   manipulation), memory_check/_pass and filter_$, children (codes 1/2 with
#   no labels), religiosity and its reverse code (no anchors in the file),
#   gender_cleaned / uni_education / vote_intention_cleaned (recodes), the two
#   theory totals and voteintentionXargumentcondition.
# `id` is the row index over the stacked studies (Study 1 first).
#
# Item text: NOT SHIPPED. The English stems and the 7 anchors are in S1
#   Appendix (journal.pone.0218333.s001); the .sav has no item labels (both
#   levels checked). Not attempted: the scale combines published gender-
#   essentialism and social-constructionism items whose source is not cited
#   item by item, so no rights reading yet.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW1 = os.environ.get("OCONNOR_RAW1", "journal.pone.0218333.s002.sav")
RAW2 = os.environ.get("OCONNOR_RAW2", "journal.pone.0218333.s003.sav")
NAME = "oconnor_2019_gender_theories"
ITEMS = [f"gendertheory_{i}" for i in range(1, 12)]
LABELLED = {"Gender": "cov_gender", "marital_status": "cov_marital_status", "religion_coded": "cov_religion",
            "education": "cov_education"}
DROPPED = ["ResponseID", "birth_year_cleaned", "cond_yes_no", "vote_intention", "vote_intention_cleaned",
           "vote_certainty", "yes_argument_strength", "no_argument_strength", "argument_strength_merged",
           "memory_check", "memory_check_pass", "filter_$", "children", "religiosity", "religiosity_reverse_coded",
           "gender_cleaned", "uni_education", "social_theory_total", "bio_theory_total",
           "voteintentionXargumentcondition"]


def load(path, study):
    df, meta = pyreadstat.read_sav(path)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen ({path}): {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 37 and txt == ["ResponseID"]
    assert df["ResponseID"].str.fullmatch(r"R_[A-Za-z0-9]{15}").all()
    out = pd.DataFrame({"cov_study": study, "cov_age": df["age_years"], "cov_political_orientation":
                        df["political_orientation"]})
    for src, cov in LABELLED.items():
        out[cov] = df[src].map(meta.variable_value_labels[src])
        assert out[cov].notna().sum() == df[src].notna().sum(), (path, src)
    for c in ITEMS:
        out[c] = df[c]
    used = set(ITEMS) | set(LABELLED) | {"age_years", "political_orientation"} | set(DROPPED)
    assert used == set(df.columns), set(df.columns) ^ used
    return out


def convert():
    df = pd.concat([load(RAW1, 1), load(RAW2, 2)], ignore_index=True)
    assert len(df) == 348 + 241
    df["id"] = range(1, len(df) + 1)
    covs = ["cov_study", "cov_gender", "cov_age", "cov_marital_status", "cov_religion",
            "cov_political_orientation", "cov_education"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(range(1, 8))
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"by study {long.groupby('cov_study')['id'].nunique().to_dict()}; dropped {DROPPED}")


if __name__ == "__main__":
    convert()
