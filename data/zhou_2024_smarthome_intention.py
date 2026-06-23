#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/Questionnaire_survey_on_the_intention_of_elderly_consumers_to_use_smart_homes/24390218
# DOI supplement: 10.1371/journal.pone.0300574.s001
# Paper DOI: 10.1371/journal.pone.0300574
# License: CC BY 4.0
# Authors: Zhou et al. (2024) — first author Chengmin Zhou
# 200 participants, 13 items (smart home use intention TAM scale, 1-5 Likert)
# Scales: PU (Perceived Usefulness, 3 items), PEOU (Ease of Use, 2 items),
#         UI (Use Intention, 2 items), ITS (Intention to Switch, 2 items),
#         PV (Perceived Value, 2 items), PR (Perceived Risk, 2 items)

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DATA_URL = "https://doi.org/10.1371/journal.pone.0300574.s001"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Download the legacy .xls file
    resp = requests.get(DATA_URL, headers=HEADERS, allow_redirects=True)
    resp.raise_for_status()

    df = pd.read_excel(io.BytesIO(resp.content), sheet_name="Sheet1")

    # Rename ID -> id
    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).copy()
    df["id"] = df["id"].astype(int)

    # Identify covariates
    cov_rename = {
        "Gender": "cov_gender",
        "Age": "cov_age",
        "Education level": "cov_education",
        "Monthly income": "cov_income",
        "Self-care ability": "cov_selfcare",
        "Living condition": "cov_living",
        "Experience": "cov_experience",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    # All 13 item columns: PU1-3, PEOU1-2, UI1-2, ITS1-2, PV1-2, PR1-2
    item_cols = ["PU1", "PU2", "PU3", "PEOU1", "PEOU2",
                 "UI1", "UI2", "ITS1", "ITS2", "PV1", "PV2", "PR1", "PR2"]

    # Melt to long format
    long = df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )

    # Clean responses — valid range 1-5
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)

    # Enforce column order: id, item, resp, cov_*
    long = long[["id", "item", "resp"] + cov_cols]

    out_name = "zhou_2024_smarthome_intention.csv"
    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)

    print(
        f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
    )


if __name__ == "__main__":
    convert()
