#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0311959
# DOI: 10.1371/journal.pone.0311959
# Paper: Geng, Q., Amini, M., Hashim, S. N. A. B., & Zhu, M. (2024). The mediating
#   roles of academic self-efficacy and learning interest in the relationship
#   between teaching style and math behavior engagement among junior high
#   school students in China. PLOS ONE 19(10): e0311959.
# Data: journal.pone.0311959.s001 (S1 File, "Data", .xlsx), 1,025 junior
#   high school students (grades 7-9), China, April-May 2024.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# FOUR output tables, one per instrument named in the paper's Measures
# section; all rated 1 (strongly disagree) to 5 (strongly agree):
#   geng_2024_teaching_style    HLS1-6, RLS1-5, CSS1-4, IES1-3 (18 items):
#       effective teaching styles scale (Him et al. 2011) -- humorous/lively,
#       rigorous/logical, caring/sharing, innovative/exploratory.
#   geng_2024_math_self_efficacy SLA1-11, SLB1-11 (22 items): academic
#       self-efficacy scale adapted from Liang (2000), learning ability and
#       learning behaviour halves.
#   geng_2024_math_interest     TSI1-5, MSI1-5, II1-7 (17 items): mathematics
#       learning interest scale (Wu & Liu 2017).
#   geng_2024_math_engagement   BE1-11 (11 items): behavioural engagement
#       subscale of Fredricks et al.'s learning engagement scale.
# The deposit's composite columns (HLS, RLS, CSS, IES, SLA, SLB, ASE, TSI,
# MIS, II, LI, BE -- means of the items) are dropped.
#
# Covariates: gender (1 = male, 2 = female: 595/430, matching the paper's
# 595 males and 430 females) and grade (1/2/3 = grades 7/8/9: 360/356/309,
# matching the paper). Dropped: Location (school location, urban/rural per
# the sampling design) and TGender (presumably teacher gender) -- bare 1/2
# codes with no codebook, so which code is which is unknown. The two share
# identical marginals (658/367) without being the same column, which makes a
# guess from the paper's counts impossible. ID is the deposit's own
# sequential row number, kept as `id`.
#
# Item text: NOT SHIPPED. Column codes only (.xlsx, no labels at any level);
#   the Chinese wording is not in the article or its SI. All four are named
#   published instruments.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("GENG_RAW", "journal.pone.0311959.s001.xlsx")
N_ROWS = 1025


def block(pfx, k):
    return [f"{pfx}{i}" for i in range(1, k + 1)]


TABLES = {
    "teaching_style": block("HLS", 6) + block("RLS", 5) + block("CSS", 4) + block("IES", 3),
    "math_self_efficacy": block("SLA", 11) + block("SLB", 11),
    "math_interest": block("TSI", 5) + block("MSI", 5) + block("II", 7),
    "math_engagement": block("BE", 11),
}
COMPOSITES = ["HLS", "RLS", "CSS", "IES", "SLA", "SLB", "ASE", "TSI", "MIS", "II", "LI", "BE"]


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 85 and txt == []
    assert df["ID"].tolist() == list(range(1, N_ROWS + 1))
    assert df["Location"].value_counts().to_dict() == df["TGender"].value_counts().to_dict() == {1: 658, 2: 367}
    assert df["Gender"].value_counts().to_dict() == {1: 595, 2: 430}
    assert df["Grade"].value_counts().to_dict() == {1: 360, 2: 356, 3: 309}
    df["id"] = df["ID"]
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_grade"] = df["Grade"] + 6
    cov_cols = ["cov_gender", "cov_grade"]
    used = {"ID", "Gender", "Grade", "Location", "TGender"} | set(COMPOSITES)
    names, total = [], 0
    for suffix, items in TABLES.items():
        used |= set(items)
        long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == {1, 2, 3, 4, 5}
        long = long[["id", "item", "resp"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {suffix} {c.name}: {c.detail[:160]}")
        name = f"geng_2024_{suffix}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={len(items)}")
    assert len(set(names)) == len(names)
    assert used == set(df.columns) - {"id", "cov_gender", "cov_grade"}, set(df.columns) - used
    print(f"total responses {total}; dropped composites {COMPOSITES} and Location/TGender")


if __name__ == "__main__":
    convert()
