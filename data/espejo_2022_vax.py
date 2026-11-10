#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/KZ66ES
# DOI (data): 10.7910/DVN/KZ66ES (also on Zenodo as 10.5281/zenodo.6603986)
# DOI (paper): 10.1186/s40359-022-00929-y
# Data: Espejo, B., & Checa, I. (2022). Vaccine Attitudes Examination (VAX)
#   scale dataset in Spain. Harvard Dataverse. Files "VAX data.csv" (data),
#   "Database codebook of variables.csv" (variable labels, including the
#   Spanish item stems) and "Variable values codebook.csv" (value labels).
# Paper: Espejo, B., Checa, I., & Martin-Carbonell, M. (2022). Psychometric
#   properties and measurement invariance of the Vaccination Attitudes
#   Examination Scale (VAX) in a Spanish sample. BMC Psychology, 10, 223.
# License: CC0 1.0, verified via the Dataverse API (latestVersion.license).
#
# Found 2026-11-10 (lane C) in a Harvard Dataverse search of JEEHP-style
#   deposits run during the repos sweep.
#
# Checked against the paper: 581 participants, mean age 30.38 (SD 13.30),
#   range 15-76, 67% women (389), five "other" and three "prefer not to
#   answer" -- all reproduce exactly.
#
# ONE output table:
#   espejo_2022_vax  Vaxx_1..Vaxx_12, the Spanish VAX (Martin & Petrie 2017),
#     1 = muy en desacuerdo ... 5 = muy de acuerdo (value codebook). Items are
#     as deposited (no reverse-scoring in the file: items 1-3 are the
#     trust-in-benefit items and run opposite to 4-12). -999 = missing
#     (5 cells) and is dropped.
# Covariates, labelled from the value codebook: gender, age (years), main
#   activity, completed studies, personal situation, vaccinated against
#   COVID-19. Dropped: the nine reasons-for-not-vaccinating checkboxes (asked
#   only of the 24 unvaccinated; a checklist, not a scale) and the free-text
#   "other reason" column.
# `id` is the row index (the file has no id column).
#
# Item text: NOT SHIPPED (held). The variable codebook carries the Spanish
#   stems, but the register's VAX row (Martin & Petrie 2017) is `hold`: a named
#   third-party instrument with no grant located. The deposit's CC0 covers the
#   depositors' data, not the instrument's wording.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ESPEJO_RAW", "VAX data.csv")
ITEMS = [f"Vaxx_{i}" for i in range(1, 13)]
LABELS = {
    "Gender": {1: "Male", 2: "Female", 3: "Other", 4: "I prefer not to answer"},
    "Activity": {1: "Study full time", 2: "Study with some intermittent job", 3: "Study and also work part-time",
                 4: "Work full time as an employee", 5: "Self employed", 6: "Unemployed looking for work",
                 7: "Inactive (unemployed without looking for work)", 8: "Retired"},
    "Studies": {1: "Unfinished primary studies or no studies", 2: "Primary studies, school graduate",
                3: "Compulsory secondary studies", 4: "Bachelor degree", 5: "University studies",
                6: "Graduate or Ph.D."},
    "SitPersonal": {1: "Single", 2: "Married/With common-law partner/Living as a couple", 3: "Divorced",
                    4: "Widow"},
    "Vaccine": {0: "No", 1: "Yes"},
}
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Activity": "cov_activity", "Studies": "cov_education",
        "SitPersonal": "cov_marital_status", "Vaccine": "cov_vaccinated"}


def convert():
    d = pd.read_csv(RAW, sep=";", encoding="utf-8-sig")
    assert d.shape == (581, 28), d.shape
    assert (d["Gender"] == 2).sum() == 389 and round(d["Age"].mean(), 2) == 30.38
    for src, lab in LABELS.items():
        assert set(d[src].dropna().unique()) <= set(lab), src
        d[src] = d[src].map(lab)
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    long = d[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    assert (long["resp"] == -999).sum() == 5
    long = long[long["resp"] != -999].dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    name = "espejo_2022_vax"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
