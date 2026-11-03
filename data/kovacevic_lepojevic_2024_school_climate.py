#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0303466
# DOI: 10.1371/journal.pone.0303466
# Paper: Kovacevic Lepojevic, M., Trajkovic, M., Mijatovic, L., Popovic-
#   Citic, B., Bukvic, L., Kovacevic, M., Parausic Marinkovic, A., &
#   Radulovic, M. (2024). The
#   relationship between teachers' disciplinary practices and school
#   bullying and students' satisfaction with school: The moderated mediation
#   effects of sex and school belonging. PLOS ONE 19(5): e0303466.
# Data: journal.pone.0303466.s001 (S1 Dataset, an old BIFF .xls written by
#   SPSS -- read with engine="xlrd"), 860 secondary-school students, grades
#   1-4, six schools in Belgrade, Serbia, April-May 2021.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# SIX output tables, one per scale block of the Serbian administration;
# item ids are the deposit's own column names, kept verbatim -- including
# its "I" vs lower-case "l" inconsistency in the Part I names (DSCSpartI1-3
# but DSCSpartl4 ..), which is the deposit's spelling, not a second item set:
#   kovacevic_lepojevic_2024_dscs_climate     DSCSpartI*/l* (36 items), Delaware
#       School Climate Survey-Student, Part I (school climate incl. safety
#       and bullying), 1 strongly disagree .. 4 strongly agree.
#       DSCSpartI25_umetnuto / DSCSpartI26_umetnuto ("umetnuto" = inserted)
#       are two items the authors added to the battery; shipped with it.
#   kovacevic_lepojevic_2024_dscs_techniques  DSCSpartll1-18 (18 items),
#       Delaware Positive, Punitive and SEL Techniques Scale, 1-4. All 18
#       administered items; the paper analyses a 13-item subset.
#   kovacevic_lepojevic_2024_dscs_sel         DSCSpartIII1-12 (12 items),
#       Delaware Social and Emotional Competencies Scale, 1-4.
#   kovacevic_lepojevic_2024_dscs_engagement  DSCSpartV1-12 (12 items),
#       Delaware Student Engagement Scale, 1-4.
#   kovacevic_lepojevic_2024_mslss_school     MSLSCskola1-8 (8 items),
#       Multidimensional Students' Life Satisfaction Scale, school domain,
#       1 strongly disagree .. 6 strongly agree.
#   kovacevic_lepojevic_2024_pssm             PSSMS1-18 (18 items),
#       Psychological Sense of School Membership, 1-5.
# All as deposited; nothing reversed. The deposit's 16 derived score
# columns (*_skor and subscale sums) are dropped.
#
# Covariates: sex (GENDER_ 1 = male / 2 = female, confirmed against the
# free-typed GENDER column "muski"/"zenski" row by row), grade (1-4) and age.
# School: SCHOOL_ (codes 1-6) is carried as `cluster_id` -- students are
# nested in six schools; the code is an identifier only. The free-typed
# SCHOOL name column (school names, no personal data) is dropped.
# N is the deposit's own respondent number, kept as `id`.
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the
#   Serbian wording is not in the article or its SI. All six are named
#   published instruments.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KOVACEVIC_RAW", "journal.pone.0303466.s001.xls")
N_ROWS = 860
PREFIXES = {  # table suffix -> (column-name predicate, scale)
    "dscs_climate": (lambda c: c.startswith(("DSCSpartI", "DSCSpartl")) and not c.startswith(
        ("DSCSpartII", "DSCSpartll", "DSCSpartI_")), range(1, 5)),
    "dscs_techniques": (lambda c: c.startswith("DSCSpartll"), range(1, 5)),
    "dscs_sel": (lambda c: c.startswith("DSCSpartIII") and not c.startswith("DSCSpartIII_"), range(1, 5)),
    "dscs_engagement": (lambda c: c.startswith("DSCSpartV") and not c.startswith("DSCSpartV_"), range(1, 5)),
    "mslss_school": (lambda c: c.startswith("MSLSCskola"), range(1, 7)),
    "pssm": (lambda c: c.startswith("PSSMS") and not c.startswith("PSSMS_"), range(1, 6)),
}
EXPECTED_K = {"dscs_climate": 36, "dscs_techniques": 18, "dscs_sel": 12, "dscs_engagement": 12,
              "mslss_school": 8, "pssm": 18}


def convert():
    df = pd.read_excel(RAW, engine="xlrd").copy()
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert set(txt) == {"SCHOOL", "GRADE", "GENDER"}
    g = df["GENDER"].astype(str).str.strip().str.lower()
    assert ((g == "muski") == (df["GENDER_"] == 1)).all() and ((g == "zenski") == (df["GENDER_"] == 2)).all()
    assert df["N"].is_unique
    df = df.copy()
    df["id"] = df["N"].astype(int)
    df["cluster_id"] = df["SCHOOL_"].astype("Int64")
    df["cov_sex"] = df["GENDER_"].map({1: "male", 2: "female"})
    df["cov_grade"] = pd.to_numeric(df["GRADE"].astype(str).str.strip(), errors="coerce").astype("Int64")
    df["cov_age"] = df["AGE"].astype("Int64")
    cov_cols = ["cov_sex", "cov_grade", "cov_age"]
    used = {"N", "SCHOOL", "SCHOOL_", "GRADE", "GENDER", "GENDER_", "AGE"}
    derived = [c for c in df.columns if "skor" in c or c.startswith(("DSCSpartI_", "DSCSpartII_", "DSCSpartIII_",
                                                                     "DSCSpartV_", "MSLSC_"))]
    used |= set(derived)
    names, total = [], 0
    for suffix, (pred, scale) in PREFIXES.items():
        items = [c for c in df.columns if pred(c) and c not in derived]
        assert len(items) == EXPECTED_K[suffix], (suffix, len(items), items)
        assert not (used & set(items)), suffix
        used |= set(items)
        long = df[["id", "cluster_id"] + cov_cols + items].melt(id_vars=["id", "cluster_id"] + cov_cols,
                                                                var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(scale), (suffix, set(long["resp"]))
        long = long[["id", "item", "resp", "cluster_id"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(scale) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {suffix} {c.name}: {c.detail[:160]}")
        name = f"kovacevic_lepojevic_2024_{suffix}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={len(items)}")
    assert len(set(names)) == len(names)
    left = set(df.columns) - used - {"id", "cluster_id"} - set(cov_cols)
    assert not left, left
    print(f"total responses {total}; dropped {len(derived)} derived score columns and SCHOOL (names)")


if __name__ == "__main__":
    convert()
