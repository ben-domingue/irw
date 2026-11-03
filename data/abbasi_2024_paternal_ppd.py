#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0303474
# DOI: 10.1371/journal.pone.0303474
# Paper: Abbasi NuH, Bilal A, Muhammad K, et al. (2024). Relationship between
#   personality traits and postpartum depression in Pakistani fathers.
#   PLOS ONE 19(5): e0303474.
# Data: OSF node w52s7 ("PPPD Data", 10.17605/OSF.IO/W52S7), file
#   "PPOst Dep.sav112.sav Complete Data Set.sav", 402 rows (400 fathers with
#   data) of fathers of a recently born baby, Pakistan.
# License: CC BY 4.0, verified on the DEPOSIT (api.osf.io/v2/nodes/w52s7:
#   public, license 563c1cf88c5e4a3877f9e96a = "CC-By Attribution 4.0
#   International"); the article is also CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# TWO output tables:
#   abbasi_2024_epds  Edinburgh Postnatal Depression Scale, 10 items, 0-3.
#     EPDS_1..EPDS_10; the source names item 4 "SPDS_4", an evident typo,
#     renamed EPDS_4 here (the only rename). Stored in SCORED direction: the
#     sum of the ten items equals the deposit's own
#     Paternal_Postpartum_Depression total on 399 of 402 rows (the other 3
#     have an item missing). EPDS_1 holds 1-3 only (no 0) as deposited.
#   abbasi_2024_bfi   Big Five Inventory, 44 items, 1-5. BFI_1..BFI_44; the
#     source names item 39 "BFI__39" (double underscore), renamed BFI_39.
#     Kept AS DEPOSITED: the deposit's own trait means (Extraversion etc.)
#     equal the RAW means of each trait's items, reverse-keyed ones included,
#     on ~98% of rows, so either the reverse-keyed items were stored already
#     reversed or the authors never reversed them -- the file cannot say which.
# Covariates: age, education (labels), wife's age, employment type (labels;
#   one free-typed "Computer" kept as given), years married, birth order of
#   the recent baby (labels).
# Dropped: the three *_in_Categories / categories_of_* columns (binned
#   duplicates of the covariates), Birth_order_of_child (raw duplicate of the
#   binned birth order, with no stated meaning for its values), Sleep_Duration
#   and Time_spend_in_home (value labels do not cover the observed codes), and
#   the six derived score columns.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. No variable labels on any item and no value labels
#   on any item (both levels checked); the wording is not in the article or on
#   the OSF node. EPDS and BFI are named published instruments.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ABBASI_RAW", "PPOst Dep.sav112.sav Complete Data Set.sav")
EDU = {"1": "undergraduate", "2": "graduate", "3": "postgraduate"}
EMP = {"1": "business", "2": "private job", "3": "government job", "Computer": "Computer"}
BORDER = {1.0: "1st or 2nd", 2.0: "3rd or 4th", 3.0: "5th or later"}
DROPPED = ["Age_in_Categories", "Wife_age_in_categories", "categories_of_marital_Duration", "Birth_order_of_child",
           "Sleep_Duration", "Time_spend_in_home", "Paternal_Postpartum_Depression", "Extraversion",
           "Agreeableness", "Conscientiousness", "Neuroticism", "Openness"]


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (402, 72), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == ["Participantseducation", "Type_of_Employment"]
    assert set(df["Type_of_Employment"]) <= set(EMP) | {""}
    df = df.rename(columns={"SPDS_4": "EPDS_4", "BFI__39": "BFI_39"})
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Participantsage"]
    df["cov_education"] = df["Participantseducation"].map(EDU)
    df["cov_wife_age"] = df["Wifesage"]
    df["cov_employment"] = df["Type_of_Employment"].map(EMP)
    df["cov_years_married"] = df["Marital_duration"]
    df["cov_baby_birth_order"] = df["Birth_order_of_baby"].map(BORDER)
    covs = ["cov_age", "cov_education", "cov_wife_age", "cov_employment", "cov_years_married", "cov_baby_birth_order"]
    blocks = {"epds": ([f"EPDS_{i}" for i in range(1, 11)], [0, 1, 2, 3]),
              "bfi": ([f"BFI_{i}" for i in range(1, 45)], [1, 2, 3, 4, 5])}
    used = {"Participantsage", "Participantseducation", "Wifesage", "Type_of_Employment", "Marital_duration",
            "Birth_order_of_baby"} | set(DROPPED)
    total = 0
    for block, (items, perm) in blocks.items():
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(perm), set(long["resp"])
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: perm for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"abbasi_2024_{block}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert used | {"id"} | set(covs) == set(df.columns), set(df.columns) - used
    print(f"total responses {total}; dropped: {DROPPED}")


if __name__ == "__main__":
    convert()
