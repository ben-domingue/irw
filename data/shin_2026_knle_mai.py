#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/IEIDXS
# DOI (data): 10.7910/DVN/IEIDXS
# DOI (paper): 10.3352/jeehp.2026.23.21
# Data: Shin, S., Lee, I., Kim, H., Song, R., Song, J.-A., Yi, H. S., Park, J.,
#   Yim, M. K., Lee, M., & Yu, S. (2026). Validity evaluation of a mock
#   examination including multimedia-assisted items for the Korean Nursing
#   Licensing Examination: a mixed-methods study with a counterbalanced design.
#   Journal of Educational Evaluation for Health Professions, 23, 21.
#   Harvard Dataverse: "Dataset 1. Binary item response data from the mock
#   examination.xlsx" and "Dataset 2. Participant characteristics and
#   post-test survey data.xlsx" (sheets Dataset_2 and Codebook).
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) in a Harvard Dataverse search of JEEHP deposits
#   during the repos sweep ("medical licensing examination").
#
# Design (paper, Methods): 515 fourth-year nursing students took an online
#   mock KNLE of 29 items, each given twice -- once as a text-based item (T)
#   and once as a multimedia-assisted item (MAI, M) with identical content --
#   in counterbalanced order: Group 1 = MT (MAI block first, 256), Group 2 = TM
#   (259). Checked against the paper: N = 515, 256/259 by group, 85.44%
#   female, mean age 24.68 -- all reproduce.
#
# TWO output tables:
#   shin_2026_knle_mai  M01..M29 and T01..T29, scored 0/1 (1 = correct), no
#     missing cells. item_family = the pair number (M07 and T07 are the same
#     item content in two formats), because the pairs are not locally
#     independent. cov_order = "MT" or "TM" (Group 1/2).
#   shin_2026_mai_perception  S01..S06, post-test perceptions of the MAIs,
#     1 = strongly disagree ... 5 = strongly agree (Codebook sheet). S07
#     (yes/no, "included content not previously learned") is a single
#     dichotomous question on a different response scale and is not shipped.
# Covariates (Codebook sheet): sex (1 = female, 2 = male, shipped as labels),
#   age (years), region of university, prior experience with MAI exams.
#   Dropped: A05_1..A05_3 (media types seen before, asked only of those with
#   prior experience; 99 = not applicable).
# `id` = the numeric part of the deposit's participant code (P001 -> 1).
#
# Item text: NOT SHIPPED. Exam items are not in the deposit. The perception
#   statements are in the Codebook sheet in English, but the survey was given
#   in Korean and the Korean wording is not deposited.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW1 = os.environ.get("SHIN_RAW1", "Dataset 1. Binary item response data from the mock examination.xlsx")
RAW2 = os.environ.get("SHIN_RAW2", "Dataset 2. Participant characteristics and post-test survey data.xlsx")
REGION = {1: "Seoul", 2: "Gyeonggi/Incheon", 3: "Gangwon", 4: "Busan/Ulsan/Daegu/Gyeongsang",
          5: "Gwangju/Jeolla", 6: "Daejeon/Chungcheong/Sejong", 7: "Jeju"}


def qc_and_write(long, items, permitted, name):
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    exam = pd.read_excel(RAW1, sheet_name="Dataset_1")
    surv = pd.read_excel(RAW2, sheet_name="Dataset_2")
    assert exam.shape == (515, 60) and surv.shape[0] == 515
    assert exam["Participants"].is_unique and set(exam["Participants"]) == set(surv["Participants"])
    assert exam["Group"].value_counts().to_dict() == {2: 259, 1: 256}
    assert (surv["A01"] == 1).sum() == 440  # 85.44% female
    d = exam.merge(surv, on="Participants", how="inner", validate="one_to_one")
    d["id"] = d["Participants"].str.replace("P", "", regex=False).astype(int)
    d["cov_order"] = d["Group"].map({1: "MT", 2: "TM"})
    d["cov_sex"] = d["A01"].map({1: "female", 2: "male"})
    d["cov_age"] = d["A02"]
    d["cov_region"] = d["A03"].map(REGION)
    d["cov_prior_mai_exam"] = d["A04"].map({1: "yes", 2: "no"})
    covs = ["cov_order", "cov_sex", "cov_age", "cov_region", "cov_prior_mai_exam"]
    assert d[covs].notna().all().all()
    os.makedirs(OUT_DIR, exist_ok=True)

    items = [f"{p}{k:02d}" for p in "MT" for k in range(1, 30)]
    long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1}
    long["item_family"] = "pair_" + long["item"].str[1:]
    long = long[["id", "item", "resp"] + covs + ["item_family"]]
    qc_and_write(long, items, [0, 1], "shin_2026_knle_mai")

    sitems = [f"S0{k}" for k in range(1, 7)]
    long = d[["id"] + covs + sitems].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + covs]
    qc_and_write(long, sitems, [1, 2, 3, 4, 5], "shin_2026_mai_perception")


if __name__ == "__main__":
    convert()
