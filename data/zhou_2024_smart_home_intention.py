#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/Questionnaire_survey_on_the_intention_of_elderly_consumers_to_use_smart_homes/24390218
# DOI: 10.1371/journal.pone.0300574.s001
# Paper DOI: 10.1371/journal.pone.0300574
# License: CC BY 4.0
# Authors: Zhou, Qian & Kaner (2024) - "A study on smart home use intention of elderly
#          consumers based on technology acceptance models"
# 200 participants, 13 items (TAM subscales: PU, PEOU, UI, ITS, PV, PR), scale 1-5
# Downloaded via DOI redirect: https://doi.org/10.1371/journal.pone.0300574.s001

import os
import io
import requests
import pandas as pd

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

# The PLOS supplement DOI resolves directly to the data file
DATA_URL = "https://doi.org/10.1371/journal.pone.0300574.s001"


def convert():
    # 1. Download data file (resolves to .xls via redirect)
    resp = requests.get(DATA_URL, headers=HEADERS, allow_redirects=True)
    resp.raise_for_status()

    df = pd.read_excel(io.BytesIO(resp.content), sheet_name="Sheet1")

    # Columns: ID, Gender, Age, Education level, Monthly income,
    #          Self-care ability, Living condition, Experience,
    #          PU1, PU2, PU3, PEOU1, PEOU2, UI1, UI2, ITS1, ITS2, PV1, PV2, PR1, PR2

    # 2. Rename ID to id
    df = df.rename(columns={"ID": "id"})

    # 3. Identify covariates
    cov_rename = {
        "Gender": "cov_gender",
        "Age": "cov_age",
        "Education level": "cov_education",
        "Monthly income": "cov_income",
        "Self-care ability": "cov_self_care",
        "Living condition": "cov_living_condition",
        "Experience": "cov_experience",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    # 4. Identify item columns
    item_cols = ["PU1", "PU2", "PU3", "PEOU1", "PEOU2",
                 "UI1", "UI2", "ITS1", "ITS2", "PV1", "PV2", "PR1", "PR2"]

    # 5. Melt to long format
    long = df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp"
    )

    # 6. Clean responses
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # Valid range 1-5 (5-point Likert)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    # 7. Enforce column order
    long = long[["id", "item", "resp"] + cov_cols]

    # 8. Save
    out_name = "zhou_2024_smart_home_intention.csv"
    out_path = os.path.join(OUT_DIR, out_name)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(out_path, index=False)

    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
