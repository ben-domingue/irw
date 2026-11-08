#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247869
# DOI: 10.1371/journal.pone.0247869
# Paper: Bergs J, Peeters K, Kortleven I, Creemers S, Ulenaers D, Desmedt M,
#   Schrooten W (2021). Translation and validation of the Dutch version of
#   the health professional education in patient safety survey amongst
#   nursing students in Belgium: A psychometric analysis. PLoS ONE 16(3):
#   e0247869.
# Data: PLOS Supporting Information S2 File (journal.pone.0247869.s002, CSV),
#   1,709 nursing and medical students at Belgian and German (Aachen)
#   institutions, academic years 2016-17 to 2018-19. S1 File (s001) is the
#   Dutch H-PEPSS questionnaire, itself released CC BY 4.0 by the
#   translators.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 5.
#
# ONE output table, bergs_2021_hpepss: all 51 H-PEPSS item columns, 1-5
#   (strongly disagree - strongly agree). Section 1 asks how confident the
#   student is in what they learned about seven patient-safety domains,
#   rated separately for the classroom (".1") and the clinical setting
#   (".2"): clinicalSafety 4, teamwork 3, communication 3, managingPS 3,
#   factors 2, responding 2, safetyculture 3 -- 20 items x 2 settings. Section
#   2 (patientsafety_1-7) covers broader patient-safety issues in the
#   curriculum; section 3 (speak_1-4) comfort speaking up. Item codes are the
#   deposit's column names (the setting kept in the code, e.g.
#   teamwork.2_1). All three sections share the one 1-5 scale and are one
#   instrument, so they ship as one table.
# Seven pairs of adjacent rows agree on all 51 items and every covariate
#   (varied, not straight-lined, answers): read as double submissions, first
#   kept (1,702 respondents).
# Covariates: gender, age, institution, programme, programme year, academic
#   year (the deposit's StartDate, e.g. "2017-2018").
# Dropped: the free-text remark (remark.PS).
# `id` is the row index.
#
# Item text: NOT SHIPPED. The S1 questionnaire carries the Dutch wording
#   under CC BY 4.0; the source instrument is the H-PEPSS (Ginsburg et al.,
#   York University), whose permission terms the translators point to.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0247869.s002"
RAW = os.environ.get("BERGS_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
COVS = {"gender": "cov_gender", "age": "cov_age", "university": "cov_institution",
        "education": "cov_programme", "educationYear": "cov_programme_year",
        "StartDate": "cov_academic_year"}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src, sep=None, engine="python")


def convert():
    df = load()
    assert df.shape == (1709, 58), df.shape
    items = list(df.columns[6:57])
    assert len(items) == 51 and items[0] == "clinicalSafety.1_1" and items[-1] == "speak_4"
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    dup = df.duplicated(subset=list(COVS) + items, keep="first")
    assert dup.sum() == 7, dup.sum()
    df = df[~dup]
    df = df.rename(columns=COVS)
    covs = list(COVS.values())
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        assert g["resp"].between(1, 5).all(), it
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:150]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "bergs_2021_hpepss.csv"), index=False)
    print(f"bergs_2021_hpepss: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
