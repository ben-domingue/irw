#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0115799
# DOI: 10.1371/journal.pone.0115799
# Paper: Li X, Guan L, Chang H, Zhang B (2014). Core Self-Evaluation and Burnout
#   among Nurses: The Mediating Role of Coping Styles. PLoS ONE 9(12): e115799.
# Data: S1 Table (journal.pone.0115799.s001, XLS, sheet "excel,数据"), 1,559
#   registered nurses at five hospitals in Shenyang, China, May-July 2013.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket); held 2026-11-02 (slice 1)
# on a date-of-birth column, released the same day by ben-domingue's ruling
# in-session: "1. yes drop".
#
# DATE OF BIRTH -- DROPPED ENTIRELY, per that ruling. `birth` (1,430 month-year
#   dates stored as day 15, 129 with other days) is not carried in any form:
#   not as a covariate, not as an age, not coarsened. `age` (a fractional age
#   computed from `birth` to the day) and `age3group` (a coarsening of it) are
#   dropped with it for the same reason.
#
# THREE output tables:
#   li_2014_nurses_cse    Core Self-Evaluation Scale (Judge et al.), Chinese
#     version, 12 items, 1 strongly disagree .. 5 strongly agree. STORED IN
#     SCORED DIRECTION: the paper says "relevant items were reverse-coded", and
#     in the deposit 65 of the 66 inter-item correlations are positive (the
#     66th, CSE4-CSE9, is -0.01; none is materially negative) and the 12
#     items sum exactly to the deposit's own `Core self-evaluation` total on
#     every row. So the reverse-keyed items arrive already reversed.
#   li_2014_nurses_scsq   Simplified Coping Style Questionnaire (Xie), 20 items,
#     0 never .. 3 very often. Coping1-12 sum exactly to `Active Coping` and
#     Coping13-20 to `Passive Coping` on every row.
#   li_2014_nurses_mbigs  Maslach Burnout Inventory - General Survey, Chinese
#     15-item version, 0 never .. 6 every day, raw answers (professional
#     efficacy not reversed; the deposit's `burnout` is the raw sum of all 15).
#     Subscales recovered by exact-sum search against the deposit's totals:
#     exhaustion burnout1-4,6; cynicism burnout8,9,13,14; professional efficacy
#     burnout5,7,10,11,12,15.
# Item codes are the source headers with trailing spaces stripped.
#
# Covariates:
#   cov_gender  0 male / 1 female. 60 vs 1,499; group 1 has the higher mean
#     exhaustion and cynicism, matching the paper's "Female nurses were more
#     easily affected by emotional exhaustion and cynicism".
#   cov_job_rank  1 junior nurse / 2 senior nurse / 3 nurse-in-charge, the
#     paper's listed order; confirmed by mean work experience 3.2 / 8.0 / 21.9
#     years and by the rank2/rank3 dummies (reference = junior nurse).
#   cov_work_experience_years  integer years.
# Dropped: `nurse number` (row sequence), birth/age/age3group (above),
#   `education` (its codes do not reconcile: the education2/education3 dummies
#   make code 3 the reference while the paper names "high school or under" as
#   reference, and the paper's "undergraduate or above had the highest
#   professional efficacy" fits code 1, the group with 15 years' mean
#   experience -- direction unrecoverable, so not carried), education2/3,
#   rank2/3, WE5group (derived), and the 7 subscale/total columns.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Column codes only, no labels at any level; neither
#   the Chinese nor the English wording is in the article or SI. MBI-GS is a
#   commercial instrument (Mind Garden).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LI2014_RAW", "journal.pone.0115799.s001.xls")
CSE = [f"CSE{i}" for i in range(1, 13)]
COP = [f"Coping{i}" for i in range(1, 21)]
MBI = [f"burnout{i}" for i in range(1, 16)]
BLOCKS = {"cse": (CSE, range(1, 6)), "scsq": (COP, range(0, 4)), "mbigs": (MBI, range(0, 7))}
DERIVED = {"burnout", "EmotionalExhaustion", "Cynicism", "Professional efficacy",
           "Active Coping", "Passive Coping", "Core self-evaluation"}
DROPPED = {"nurse number", "birth", "age", "age3group", "education", "education2", "education3",
           "rank2", "rank3", "WE5group"} | DERIVED


def convert():
    df = pd.read_excel(RAW)
    df.columns = [c.strip() for c in df.columns]
    assert df.shape == (1559, 67), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    # the scored-direction and subscale claims in the header
    assert (df[CSE].sum(axis=1) == df["Core self-evaluation"]).all()
    assert df[CSE].corr().values.min() > -0.05  # 65 of 66 positive, CSE4-CSE9 -0.01
    assert (df[COP[:12]].sum(axis=1) == df["Active Coping"]).all()
    assert (df[COP[12:]].sum(axis=1) == df["Passive Coping"]).all()
    assert (df[MBI].sum(axis=1) == df["burnout"]).all()
    assert ((df["jobrank"] == 2) == df["rank2"]).all() and ((df["jobrank"] == 3) == df["rank3"]).all()

    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["gender"].map({0: "male", 1: "female"})
    df["cov_job_rank"] = df["jobrank"].map({1: "junior nurse", 2: "senior nurse", 3: "nurse-in-charge"})
    df["cov_work_experience_years"] = df["workexperience"]
    covs = ["cov_gender", "cov_job_rank", "cov_work_experience_years"]
    assert df[covs].notna().all().all()
    used = {"gender", "jobrank", "workexperience"} | DROPPED

    names, total = [], 0
    for block, (items, ok) in BLOCKS.items():
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert long["resp"].isin(list(ok)).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(ok) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"li_2014_nurses_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    src = set(df.columns) - {"id"} - set(covs)
    assert used == src, (src - used, used - src)
    print(f"total responses {total}")


if __name__ == "__main__":
    convert()
