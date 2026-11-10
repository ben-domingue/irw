#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WBTRMW
# DOI (data): 10.7910/DVN/WBTRMW
# DOI (paper): 10.3352/jeehp.2019.16.25
# Data: Gelston, C. D., & Patnaik, J. L. (2019). Ophthalmology training and
#   competency levels in caring for patients with ophthalmic complaints among
#   United States internal medicine, emergency medicine, and family medicine
#   residents. Journal of Educational Evaluation for Health Professions, 16,
#   25. Harvard Dataverse "Jeehp_16_25_raw data.tab" (REDCap export).
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper (Table 1): 1,025 residents; internal medicine
#   412 / emergency 342 / family 271 (residency_program 2/3/1); male 528,
#   female 476 (gender 1/2); race codes 1-7 match the table's counts (White
#   601, Hispanic 72, African-American 26, Asian/Pacific Islander 174,
#   Native American 3, multiple 35, other 74) -- all reproduce.
#
# ONE output table:
#   gelston_2019_ophtho_confidence  32 items, confidence on a 5-point scale
#     from "not confident" (1) to "very confident" (5) (paper, Methods):
#     8 exam skills (care_va visual acuity ... care_fdt), 20 ocular
#     conditions (blepharitis ... sjogrens) and 4 drug classes (meds_*).
#     Item codes are the REDCap variable names.
# Covariates (labels from the paper's Table 1): residency program, PGY year,
#   gender, race/ethnicity, US/international medical school (code as
#   deposited), ophthalmology hours in medical school and in residency
#   (codes as deposited). Dropped: the REDCap timestamp and the free-text
#   "suggestions" column.
# `id` is the deposit's sid.
#
# Item text: NOT SHIPPED. Variable names only in the deposit.

import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")


def write(d, items, permitted, name, covs, codes=None, drop_values=()):
    codes = codes or items
    sub = d[["id"] + covs + items].rename(columns=dict(zip(items, codes)))
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[~long["resp"].isin(drop_values)]
    assert (long["resp"] == np.floor(long["resp"])).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted), set(long["resp"])
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

RAW = os.environ.get("GELSTON_RAW", "Jeehp_16_25_raw data.tab")
ITEMS = ["care_va", "care_pupils", "care_em", "care_cvf", "care_iop", "care_sle", "care_do", "care_fdt",
         "blepharitis", "chalazion", "cellulitis", "herpes", "conjunctivitis", "scleritis", "pterygium",
         "hemorrhage", "abrasion", "ulcer", "keratitis", "dryeye", "poag", "acg", "cataract", "diabret",
         "hyperret", "ted", "rheumat", "sjogrens", "meds_antibiotics", "meds_steroids", "meds_glaucoma",
         "meds_nsaids"]
PROGRAM = {1: "family medicine", 2: "internal medicine", 3: "emergency medicine"}
GENDER = {1: "male", 2: "female"}
RACE = {1: "White", 2: "Hispanic", 3: "African-American", 4: "Asian/Pacific Islander", 5: "Native American",
        6: "Multiple", 7: "Other"}


def convert():
    d = pd.read_csv(RAW)
    assert len(d) == 1025 and d["sid"].is_unique
    assert d["residency_program"].value_counts().to_dict() == {2: 412, 3: 342, 1: 271}
    assert (d["gender"] == 1).sum() == 528 and (d["gender"] == 2).sum() == 476
    d["id"] = d["sid"]
    d["cov_program"] = d["residency_program"].map(PROGRAM)
    d["cov_pgy"] = d["residency_year"]
    d["cov_gender"] = d["gender"].map(GENDER)
    d["cov_race"] = d["race_eth"].map(RACE)
    d["cov_medschool_where"] = d["medschool_where"]
    d["cov_medschool_ophtho_hours"] = d["medschool_hours"]
    d["cov_residency_ophtho_hours"] = d["residency_hours"]
    covs = ["cov_program", "cov_pgy", "cov_gender", "cov_race", "cov_medschool_where",
            "cov_medschool_ophtho_hours", "cov_residency_ophtho_hours"]
    write(d, ITEMS, [1, 2, 3, 4, 5], "gelston_2019_ophtho_confidence", covs)


if __name__ == "__main__":
    convert()
