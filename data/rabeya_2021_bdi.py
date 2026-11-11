#!/usr/bin/env python3
# Source: https://zenodo.org/records/5808314
# DOI (data): 10.5281/zenodo.5808314
# DOI (paper): 10.12688/f1000research.108557.3
# Paper: Rabeya R, Alam N, Sonia ZF, Mohajon DR, Arafat Y, Hasan MK, Hawlader
#   MDH (2023). Depressive symptoms and their sociodemographic determinants
#   among people living with HIV/AIDS in Bangladesh: a cross-sectional study.
#   F1000Research 11:239 (version 3).
# Data: Rabeya, M. R., Alam, M. N., Sonia, Z. F., & Mohajon, D. R. (2021).
#   HIV/AIDS-Depressive symptoms dataset. Zenodo.
#   Dataset_HIV_Depression_Study.xlsx: 338 people living with HIV/AIDS at
#   CARE Bangladesh drop-in centres, Dhaka, 2020.
# License: CC BY 4.0 (Zenodo record). Paper CC BY 4.0.
# Codebook: the Zenodo record's description (covariate codes and the 0-3 BDI
#   scoring); no separate file.
#
# Worked in overnight lane C 2026-11-10 (repos sweep); held that night, ruled
# ship by Ben 2026-11-11.
#
# ONE table: rabeya_2021_bdi, the 21 Beck Depression Inventory-II items
#   (named by symptom in the deposit -- Sadness ... Loss_Interest_Sex --
#   which match BDI-II item content and order), 0-3. Items are coded bdi1..bdi21
#   by BDI-II item number, tied to the deposit's column names by the NAMES list
#   below (asserted against the file's column order): the symptom names
#   themselves trip the covariate lint ("loss_interest_sex" reads as sex).
#
# DATA NOTE -- SEVERITY BANDS DO NOT REPRODUCE: N = 338 and the sex split
#   297 / 20 / 21 match the paper exactly, so this is the analysed sample. But
#   the paper's BDI severity bands (cut-offs 0-9 / 10-16 / 17-29 / 30-63)
#   give 1.8 / 5.6 / 30.5 / 62.1%, while the deposit's item sums give
#   2.4 / 13.3 / 38.8 / 45.6%. Shipped as deposited; the item data are the
#   record, and the mismatch is either in the paper's banding or in how its
#   totals were computed.
#
# Covariates: age (years), sex, education, occupation, religion, marital
#   status, family type, family size band, monthly income band, alcohol,
#   smoking, drug use (yes/no), years infected with HIV (band) -- all decoded
#   from the codes in the Zenodo description.
# Not shipped: Age_Range (a banding of age); Receiving_HIV_Treatment, whose
#   values are 1/2 only while the description gives it the three-level
#   duration code list, so its meaning is not documented.
# `id` = the deposit's Serial_No. (1..338).
#
# Item text: NOT SHIPPED. BDI-II is Pearson-copyrighted; the deposit has
#   symptom names only.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://zenodo.org/records/5808314/files/Dataset_HIV_Depression_Study.xlsx?download=1"
RAW = os.environ.get("RABEYA2021_RAW")
NAME = "rabeya_2021_bdi"

NAMES = ["Sadness", "Pesimism", "Past_Failure", "Loss_of_Pleasure", "Guilty_Feelings",
         "Punishment_Feelings", "Self_Dislike", "Self_Criticalness", "Suicidal_Thoughts_or_Wishes",
         "Crying", "Agitation", "Loss_of_Interest", "Indecisiveness", "Worthlessness",
         "Loss_of_Energy", "Changes_in_Sleeping_Pattern", "Irritability", "Changes_in_Appetite",
         "Concentration_Difficulty", "Tiredness_or_Fatigue", "Loss_Interest_Sex"]
CODE = {n: f"bdi{k}" for k, n in enumerate(NAMES, 1)}
YN = {1: "yes", 2: "no"}
CODES = {
    "Sex": ("cov_sex", {1: "male", 2: "female", 3: "transgender"}),
    "Education": ("cov_education", {1: "illiterate", 2: "below secondary", 3: "undergraduate and above"}),
    "Occupation": ("cov_occupation", {1: "unemployed/housewife/other", 2: "employed", 3: "student"}),
    "Religion": ("cov_religion", {1: "Muslim", 2: "Hindu"}),
    "Marital_Status": ("cov_marital_status", {1: "married", 2: "unmarried", 3: "divorced or separated"}),
    "Types_of_Family": ("cov_family_type", {1: "nuclear", 2: "joint"}),
    "Family_Size": ("cov_family_size", {1: "single", 2: "2-5", 3: "6+"}),
    "Monthly_Income": ("cov_income_bdt", {1: "<10000", 2: "11000-20000", 3: "21000+"}),
    "Alcohol_Consumption": ("cov_alcohol", YN),
    "Smokin_Habit": ("cov_smoking", YN),
    "Drug_Abuse": ("cov_drug_use", YN),
    "HIV_Infected_Duration": ("cov_hiv_duration", {1: "<1 year", 2: "1-2 years", 3: ">2 years"}),
}


def load():
    if RAW:
        return pd.read_excel(RAW)
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    from io import BytesIO
    return pd.read_excel(BytesIO(r.content))


def main():
    d = load()
    assert d.shape == (338, 37), d.shape
    items = list(d.columns[16:])
    assert items == NAMES, items
    assert d[items].isin([0, 1, 2, 3]).all().all()
    assert (d["Sex"].value_counts().to_dict() == {1: 297, 3: 21, 2: 20})
    s = d[items].sum(axis=1)
    bands = pd.cut(s, [-1, 9, 16, 29, 63]).value_counts(normalize=True, sort=False).round(3).tolist()
    print(f"item-sum severity bands (paper: 1.8/5.6/30.5/62.1%): {bands}")
    d["id"] = d["Serial_No."]
    assert d["id"].is_unique
    d["cov_age"] = d["Age"]
    for src, (dst, lab) in CODES.items():
        assert set(d[src].dropna()) <= set(lab), src
        d[dst] = d[src].map(lab)
    covs = ["cov_age"] + [dst for dst, _ in CODES.values()]
    long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["item"] = long["item"].map(CODE)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    pv = {CODE[i]: {0, 1, 2, 3} for i in items}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(long, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    main()
