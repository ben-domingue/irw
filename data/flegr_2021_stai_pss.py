#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.14651490.v1
# DOI (data): 10.6084/m9.figshare.14651490.v1
# Data: Flegr, J. (2021). Data for the study "Latent toxoplasmosis is
#   associated with a higher level of perceived stress in men but not women,
#   is not associated with anxiety and is associated with worse mental health".
#   figshare, DataAnxietyStress.csv (semicolon-separated Qualtrics export).
# License: CC BY 4.0, verified on the figshare API (api.figshare.com/v2/articles/14651490).
#
# Found 2026-11-10 (hour-1110-b) from lane C's sweep-2 leads (repos_leads_2026-11-10c2.csv).
#
# Czech/Slovak nonclinical online sample, 2018-2021; the deposit holds the 776
# subjects that survived the authors' filters (614 Toxoplasma-free, 162
# infected: both reproduce from the toxoplasmosis column). TWO output tables:
#   flegr_2021_stai_trait  STAI X-2 (trait anxiety), STAI1..STAI20, 1-4.
#   flegr_2021_pss         Perceived Stress Scale, PSS1..PSS10, 1-5.
#   Items ship RAW. The description says items 1, 6, 7, 10, 13, 16, 19 (STAI)
#   and 4, 5, 7, 8 (PSS) were inverted before averaging; in the file exactly
#   those items have negative item-rest correlations, so they are stored
#   unreversed. (The deposit's STAI/PSS total columns equal 20x / 10x the RAW
#   item means, not the inverted ones; they are dropped either way.)
#   Blank cells (skipped questions) are dropped.
# Covariates: age, and the deposit's numeric codes for sex (1/2; 156 / 620),
#   education (1-8), toxoplasmosis (1 = free, 2 = infected; 614/162 per the
#   description), Rh (1/2), self-rated physical and mental conditions (1-6).
#   Sex, education and Rh labels are not in the deposit, so they ship as codes.
# Dropped: StartDate, EndDate, Progress, Duration, ResponseId (Qualtrics
#   response id), order. `id` is the row index.
#
# Item text: not shipped -- codes only; STAI is copyrighted (Mind Garden).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("FLEGR_RAW", "DataAnxietyStress.csv")
COVS = ["cov_age", "cov_sex_code", "cov_education_code", "cov_toxoplasmosis", "cov_rh_code",
        "cov_physical_conditions", "cov_mental_conditions"]


def convert():
    d = pd.read_csv(RAW, sep=";", encoding="utf-8-sig")
    assert d.shape == (776, 45)
    assert d["toxoplasmosis"].value_counts().to_dict() == {1: 614, 2: 162}
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["age"]
    d["cov_sex_code"] = d["sex"]
    d["cov_education_code"] = d["education"]
    d["cov_toxoplasmosis"] = d["toxoplasmosis"].map({1: "free", 2: "infected"})
    d["cov_rh_code"] = d["Rh"]
    d["cov_physical_conditions"] = d["physicalConditions"]
    d["cov_mental_conditions"] = d["mentalConditions"]
    for prefix, n, top, name in [("STAI", 20, 4, "flegr_2021_stai_trait"), ("PSS", 10, 5, "flegr_2021_pss")]:
        items = [f"{prefix}{i}" for i in range(1, n + 1)]
        long = d[["id"] + COVS + items].melt(id_vars=["id"] + COVS, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        permitted = list(range(1, top + 1))
        assert set(long["resp"]) <= set(permitted)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + COVS]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: permitted for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
