#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/V83FXD
# DOI: 10.7910/dvn/v83fxd
# License: CC0
# Dataset: Police Violence and Public Perceptions (experimental survey)
# 2759 participants, experimental design with 3 treatment conditions
# Scales:
#   - blame: blame_clark, blame_officers, blame_hahn, blame_steinberg,
#             blame_schubert, blame_brown, blame_senators (1-7)
#   - law: law_knows, law_agree (1-4), law_sheriff, law_da (1-3)
#   - trust: trust_spdleaders (1-5)
# treat_info: 1=control, 2=treatment A, 3=treatment B (3-level, stored as cov_)

import os
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID = 3380835  # police1.xlsx
URL = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    resp = requests.get(URL, headers=HEADERS)
    resp.raise_for_status()

    from io import BytesIO
    df = pd.read_excel(BytesIO(resp.content))

    # Rename id and covariates
    df = df.rename(columns={"idno": "id"})

    # Treatment condition (3-level: 1=control, 2=treatment A, 3=treatment B)
    # Cannot encode as binary treat; store as covariate
    df = df.rename(columns={
        "county": "cov_county",
        "treat_info": "cov_treat_condition",
        "partyid": "cov_partyid",
        "race": "cov_race",
        "educ": "cov_educ",
        "ideo_rating": "cov_ideo_rating",
        "work4law": "cov_work4law",
    })

    cov_cols = ["cov_county", "cov_treat_condition", "cov_partyid",
                "cov_race", "cov_educ", "cov_ideo_rating", "cov_work4law"]

    # Scale 1: blame items (1-7 scale)
    blame_cols = ["blame_clark", "blame_officers", "blame_hahn",
                  "blame_steinberg", "blame_schubert", "blame_brown", "blame_senators"]

    long_blame = df[["id"] + cov_cols + blame_cols].melt(
        id_vars=["id"] + cov_cols,
        value_vars=blame_cols,
        var_name="item",
        value_name="resp"
    )
    long_blame["resp"] = pd.to_numeric(long_blame["resp"], errors="coerce")
    long_blame = long_blame.dropna(subset=["resp"]).reset_index(drop=True)
    long_blame = long_blame[(long_blame["resp"] >= 1) & (long_blame["resp"] <= 7)].reset_index(drop=True)
    long_blame = long_blame[["id", "item", "resp"] + cov_cols]

    name_blame = "clifford_2018_police_blame.csv"
    long_blame.to_csv(os.path.join(OUT_DIR, name_blame), index=False)
    print(f"{name_blame}: rows={len(long_blame)} ids={long_blame['id'].nunique()} "
          f"items={long_blame['item'].nunique()} resp={long_blame['resp'].min():.0f}-{long_blame['resp'].max():.0f}")

    # Scale 2: law items — law_knows and law_agree (1-4 scale)
    # Note: law_sheriff and law_da are 1-3 scale — different instrument, separate file
    law_4_cols = ["law_knows", "law_agree"]
    long_law4 = df[["id"] + cov_cols + law_4_cols].melt(
        id_vars=["id"] + cov_cols,
        value_vars=law_4_cols,
        var_name="item",
        value_name="resp"
    )
    long_law4["resp"] = pd.to_numeric(long_law4["resp"], errors="coerce")
    long_law4 = long_law4.dropna(subset=["resp"]).reset_index(drop=True)
    long_law4 = long_law4[(long_law4["resp"] >= 1) & (long_law4["resp"] <= 4)].reset_index(drop=True)
    long_law4 = long_law4[["id", "item", "resp"] + cov_cols]

    name_law4 = "clifford_2018_police_law_support.csv"
    long_law4.to_csv(os.path.join(OUT_DIR, name_law4), index=False)
    print(f"{name_law4}: rows={len(long_law4)} ids={long_law4['id'].nunique()} "
          f"items={long_law4['item'].nunique()} resp={long_law4['resp'].min():.0f}-{long_law4['resp'].max():.0f}")

    # Scale 3: trust in police leaders (1-5 scale, single item)
    trust_cols = ["trust_spdleaders"]
    long_trust = df[["id"] + cov_cols + trust_cols].melt(
        id_vars=["id"] + cov_cols,
        value_vars=trust_cols,
        var_name="item",
        value_name="resp"
    )
    long_trust["resp"] = pd.to_numeric(long_trust["resp"], errors="coerce")
    long_trust = long_trust.dropna(subset=["resp"]).reset_index(drop=True)
    long_trust = long_trust[(long_trust["resp"] >= 1) & (long_trust["resp"] <= 5)].reset_index(drop=True)
    long_trust = long_trust[["id", "item", "resp"] + cov_cols]

    name_trust = "clifford_2018_police_trust.csv"
    long_trust.to_csv(os.path.join(OUT_DIR, name_trust), index=False)
    print(f"{name_trust}: rows={len(long_trust)} ids={long_trust['id'].nunique()} "
          f"items={long_trust['item'].nunique()} resp={long_trust['resp'].min():.0f}-{long_trust['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
