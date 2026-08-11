#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0334214
# DOI: 10.1371/journal.pone.0334214
# SI file (S1 File): https://doi.org/10.1371/journal.pone.0334214.s001
#
# Zhao C, Tang M, Wang C (2025) The impact of digital literacy on the urban
# integration of migrant workers. PLoS One 20(10): e0334214.
#
# Data source is CFPS (China Family Panel Studies) 2016/2018 waves,
# restricted to rural-hukou individuals aged 16+ doing non-agricultural
# urban work. The raw file mixes genuine per-respondent survey items with
# several already-computed composite indices (e.g. "Digital literacy",
# "Urban integration", "Economic/Social/Psychological integration" - all
# entropy-weighted composites per the paper's Methods). Only the seven raw
# digital-literacy indicator items described in the paper are shipped as
# `resp`:
#   - two binary device-access items ("Do you use a mobile phone" / "...a
#     computer", 0/1)
#   - five 7-point frequency items (0=never .. 6=almost every day) for
#     internet use in learning/work/socializing/entertainment/business
# The "Digital literacy" composite column itself is the entropy-weighted
# aggregate of exactly these seven items and is dropped (it's an index, not
# a response). All other single-item outcome/background measures (life
# satisfaction, social status, resilience, etc.) and other composite
# indices are carried as `cov_*` (covariates don't need to be raw items).
#
# `pid` repeats across the 2016/2018 waves for panel respondents (378 of
# 6580 rows), so a `wave` column (= survey year) is used; duplicate
# id+item pairs across waves are expected and valid per the data standard.
# No PII (names/DOB/IP/GPS) present in the file.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?id=10.1371/journal.pone.0334214.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = {
    "Do you use a mobile phone": "mobile_phone",
    "Do you use a computer": "computer",
    "Digital learning": "digital_learning",
    "Digital work": "digital_work",
    "Digital social": "digital_social",
    "Digital entertainment": "digital_entertainment",
    "Digital commerce": "digital_commerce",
}

COV_COLS = {
    "labor contract": "cov_labor_contract",
    "Logarithm of wage income": "cov_wage_income_log",
    "Social status": "cov_social_status",
    "social relations": "cov_social_relations",
    "Life satisfaction": "cov_life_satisfaction",
    "Confidence in future development": "cov_confidence_future",
    "Urban integration": "cov_urban_integration",
    "Economic integration": "cov_economic_integration",
    "Social integration": "cov_social_integration",
    "Psychological integration": "cov_psychological_integration",
    "Information acquisition": "cov_information_acquisition",
    "Favors and gifts(logarithm)": "cov_favors_gifts_log",
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Between generations": "cov_new_generation",
    "Marriage": "cov_marriage",
    "Educational level": "cov_education_level",
    "Heterogeneity of Educational Level": "cov_education_heterogeneity",
    "Party": "cov_party_member",
    "Health condition": "cov_health",
    "Resilience": "cov_resilience",
    "Annual household income (logarithm)": "cov_household_income_log",
    "Family size": "cov_family_size",
    "Annual household expenditure (logarithm)": "cov_household_expenditure_log",
    "Is it the east": "cov_east_region",
    "province": "cov_province",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    raw = fetch_raw()

    raw = raw.rename(columns={"pid": "id", "year": "wave"})
    raw = raw.dropna(subset=["id"]).reset_index(drop=True)

    item_cols = list(ITEM_COLS.keys())
    cov_cols = [c for c in COV_COLS if c in raw.columns]

    df = raw.rename(columns=ITEM_COLS).rename(columns=COV_COLS)
    item_names = list(ITEM_COLS.values())
    cov_names = [COV_COLS[c] for c in cov_cols]

    long = df.melt(
        id_vars=["id", "wave"] + cov_names,
        value_vars=item_names,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "wave"] + cov_names
    long = long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    out_name = "zhao_2025_digital_literacy.csv"
    long.to_csv(os.path.join(OUT_DIR, out_name), index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
