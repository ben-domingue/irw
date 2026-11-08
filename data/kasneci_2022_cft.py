#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264316
# DOI: 10.1371/journal.pone.0264316
# Paper: Kasneci E, Kasneci G, Trautwein U, Appel T, Tibus M, Jaeggi SM,
#   Gerjets P (2022). Do your eye movements reveal your performance on an IQ
#   test? A study linking eye movements and socio-demographic information to
#   fluid intelligence. PLoS ONE 17(3): e0264316.
# Data: Harvard Dataverse doi:10.7910/DVN/JGOCKI ("TueEyeQ"), file
#   cft_full.tab (datafile 4197145, original format), 315 university-age
#   adults (18-30) in Tuebingen who took the CFT 20-R culture-fair
#   intelligence test while their eye movements were recorded. Long format
#   already: one row per subject x task, 54 tasks.
# License: CC0 1.0 (the Dataverse dataset's licence field).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 5.
#
# ONE output table, kasneci_2022_cft: `cft_task` scored 1 correct / 0 wrong
#   for the 54 CFT 20-R tasks in the deposit (15 cft_rows_*, 15 cft_clas_*,
#   14 cft_mat1_* without 11, 10 cft_mat2_* without 3 -- the deposit's own
#   subtest names); item codes are the deposit's task_id. cft_rows_4_e is
#   answered correctly by all 313 who reached it. Blank cells are tasks
#   not reached or not answered in the time limit (most of them at the end of
#   each timed subtest) and are dropped, not scored 0. The per-subject sum of
#   the scored tasks equals the deposit's cft_sum_full for all 315 subjects
#   (asserted). The deposit's "_e" suffix on a few task ids is kept as given.
# Covariates: age, primary field of study (the deposit's English text).
# Dropped: the subject code (replaced by the row index of the subject); the
#   gender and handedness codes (1/2, unlabelled in the file); the parental
#   language/education/occupation, school grades, media-use, gaming and
#   leisure blocks (background covariates, not part of the test); the eye
#   tracking files (no per-task response time in this table).
#
# Item text: NOT SHIPPED. The CFT 20-R is a commercial test (Hogrefe); its
#   items are figures and are not in the deposit.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://dataverse.harvard.edu/api/access/datafile/4197145?format=original"
RAW = os.environ.get("KASNECI_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    src = RAW
    if not src:
        import io
        r = requests.get(URL, headers=HDR, timeout=300)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src)


def convert():
    df = load()
    assert df.shape == (17010, 79), df.shape
    assert df["subject"].nunique() == 315 and df["task_id"].nunique() == 54
    assert not df.duplicated(["subject", "task_id"]).any()
    tot = df.groupby("subject").agg(s=("cft_task", "sum"), f=("cft_sum_full", "first"))
    assert (tot["s"] == tot["f"]).all()
    subj = {s: i + 1 for i, s in enumerate(df["subject"].drop_duplicates())}
    df["id"] = df["subject"].map(subj)
    df["item"] = df["task_id"]
    df["resp"] = df["cft_task"]
    df["cov_age"] = df["age"]
    df["cov_study_field"] = df["study_subject_primary"]
    covs = ["cov_age", "cov_study_field"]
    long = df.loc[df["resp"].notna(), ["id", "item", "resp"] + covs].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1}
    checks = run_qc(long, permitted_values={c: [0, 1] for c in long["item"].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:150]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "kasneci_2022_cft.csv"), index=False)
    print(f"kasneci_2022_cft: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
