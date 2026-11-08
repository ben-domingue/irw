#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295105
# DOI: 10.1371/journal.pone.0295105
# Paper: Zhao Y, Liu F, Lin P, Tu Z, Wu B (2024). Sleep quality and mental
#   health among Chinese nurses after the COVID-19 pandemic: A moderated
#   model. PLoS ONE 19(5): e0295105.
# Data: PLOS Supporting Information S1 Raw data (journal.pone.0295105.s001,
#   .xlsx), 1,219 nurses in Quanzhou, China, surveyed September 2022.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 5.
#
# TWO output tables:
#   zhao_2024_phq9   PHQ1-PHQ9
#   zhao_2024_gad7   GAD1-GAD7
# Both are stored 1-4 in the deposit (the published 0-3 scoring plus one):
#   on every row the item sum minus 9 (PHQ) or minus 7 (GAD) equals the
#   deposit's own total, asserted below. Kept 1-4 as deposited.
# Covariates, labelled from the paper's Table 1 (the counts match code by
#   code): gender (1 male = 48, 2 female = 1,171), age, work experience in
#   years, education (1 college = 628; 2 and 3 together are the paper's 591
#   "undergraduate"), married (1 = 876), has children (2 = 811 yes), lives
#   with family (1 = 737 yes), frontline work (1 = 809 yes).
# Dropped: the PSQI (only the seven derived component scores are
#   deposited, not the 19 raw questions) and the SSRS social support scale
#   (its item-6/item-8 source checklists carry a -3 code and the scale's
#   scoring mixes counts and ratings); all total scores.
# `id` is the deposit's ID (1-1219, a row number).
#
# Item text: NOT SHIPPED. PHQ-9 and GAD-7 are published instruments; the
#   wording is not in the deposit.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0295105.s001"
RAW = os.environ.get("ZHAO_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
YN = {"yes": "yes", "no": "no"}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src)


def convert():
    df = load()
    assert df.shape == (1219, 68), df.shape
    assert df["ID"].is_unique
    df["id"] = df["ID"].astype(int)
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_age"] = df["Age"]
    df["cov_work_experience_years"] = df["Work experience"]
    df["cov_education"] = df["Education"].map({1: "college", 2: "undergraduate", 3: "undergraduate"})
    df["cov_married"] = df["Marital status"].map({1: "married", 2: "other"})
    df["cov_children"] = df["Children"].map({2: "yes", 1: "no"})
    df["cov_lives_with_family"] = df["Living with family members"].map({1: "yes", 0: "no"})
    df["cov_frontline"] = df["Frontline work"].map({1: "yes", 2: "no"})
    covs = [c for c in df.columns if c.startswith("cov_")]
    assert df[covs].notna().all().all()
    assert (df["cov_gender"] == "female").sum() == 1171 and (df["cov_children"] == "yes").sum() == 811
    for name, pre, n, tot in [("phq9", "PHQ", 9, "PHQ total score"), ("gad7", "GAD", 7, "GAD total score")]:
        items = [f"{pre}{i}" for i in range(1, n + 1)]
        assert ((df[items] - 1).sum(axis=1) == df[tot]).all()
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4}
        long = long[["id", "item", "resp"] + covs]
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = f"zhao_2024_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
