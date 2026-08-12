#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0277247
# DOI: 10.1371/journal.pone.0277247
#
# Mistry et al. (2022), "Changes in loneliness prevalence and its
# associated factors among Bangladeshi older adults: Findings from two
# repeated cross-sectional studies." PLOS ONE. CC BY 4.0. N=2077 (1032 in
# a 2020 phone survey, 1045 in a separate, independently-sampled 2021
# phone survey -- an explicitly *repeated cross-sectional* design, not a
# panel of the same respondents; the paper's own abstract states this
# directly, so `round` is carried as a covariate, not `wave`, per
# datastandard.md's "same focal unit at multiple time points" definition
# of wave).
#
# 8 binary yes/no items forming a COVID-19-era hardship/concern battery
# (memory/concentration problems, comorbidity, COVID-19 concern,
# overwhelm, food difficulty, medicine difficulty, earning difficulty,
# routine medical care difficulty), confirmed via each column's own
# Stata value labels to be consistently coded 1=no problem, 2=problem
# present across all 8 -- remapped to 0/1. Demographic columns
# (division/urban_rural/sex/age_rec/marital_status/family size/income/
# occupation/living situation/education/distance-to-care) are covariates,
# excluded from the item battery. `lone` (the paper's loneliness outcome,
# from the 3-item UCLA Loneliness Scale collapsed to a single binary
# variable in this de-identified file) is a single-item construct and is
# not shipped as its own file per the no-single-item-scale policy; kept
# as a covariate for downstream context. No PII (division/region-level
# geography only, no addresses or names).

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0277247.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [
    "memory", "comorbidity", "concern", "overwhelmed",
    "difficulty_food", "difficulty_medicine", "difficulty_earning",
    "routine_medical_difficult",
]

COV_RENAME = {
    "q61_division": "cov_division",
    "q6_urban_rural": "cov_urban_rural",
    "q9_sex": "cov_sex",
    "round": "cov_survey_round",
    "age_rec": "cov_age_group",
    "marital_status": "cov_marital_status",
    "family_size_rec": "cov_family_size",
    "family_income": "cov_family_income",
    "occu": "cov_employment",
    "living_alone": "cov_living_alone",
    "q13_read_write": "cov_literate",
    "lone": "cov_lonely",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_stata(io.BytesIO(r.content), convert_categoricals=False)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    for c in ITEM_COLS:
        df[c] = df[c].map({1.0: 0, 2.0: 1})

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 1)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_path = OUT_DIR / "mistry_2022_hardship.csv"
    long.to_csv(out_path, index=False)
    print(f"mistry_2022_hardship: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
