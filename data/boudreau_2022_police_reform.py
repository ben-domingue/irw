#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OXIMKR
# DOI: 10.7910/DVN/OXIMKR
# Authors: Boudreau, Cheryl; MacKenzie, Scott; Simmons, Daniel J.
# License: CC0
# 1633 participants, 4 police reform policy items (certif, carotid, review, interv), 1-5 Likert
# Experimental design: treat2_lawenf (0=control, 1-4=treatment conditions)
# Items measure support for specific police reform proposals on a 5-point scale.

import os
import io
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

DATAVERSE_FILE_ID = 6381227  # lawenf_1.xlsx


def convert():
    headers = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
    url = f"https://dataverse.harvard.edu/api/access/datafile/{DATAVERSE_FILE_ID}"
    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name=0)

    # Person ID: svyid is a unique integer per respondent
    df = df.rename(columns={"svyid": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    # Treatment variable: treat2_lawenf (0=control, 1-4=treatment)
    # Recode: 0=control, 1-4=treatment (collapse to binary treat flag)
    # Per the data standard, treat should be 0/1. The 5 conditions are:
    #   0 = control (no endorsement), 1-4 = different endorsement/opposition conditions
    # We preserve the original multi-level coding in a cov_ column and set treat=1
    # for any non-control assignment, as the standard requires 0/1 binary treat.
    # Actually, to preserve the original experimental conditions for downstream use,
    # we store treat2_lawenf as cov_treat_condition and set treat to 0/1.
    df["treat"] = (df["treat2_lawenf"] > 0).astype(int)
    df = df.rename(columns={"treat2_lawenf": "cov_treat_condition"})

    # Covariates
    cov_rename = {
        "dem_gender": "cov_gender",
        "dem_latino": "cov_latino",
        "dem_race": "cov_race",
        "dem_educ": "cov_educ",
        "dem_age": "cov_age",
        "dem_income": "cov_income",
        "dem_ideoly": "cov_ideology",
        "dem_lawenf": "cov_law_enforce_contact",
        "race2": "cov_race2",
        "party2": "cov_party",
        "blm_support": "cov_blm_support",
        "attention": "cov_attention",
        "add": "cov_add",
    }
    df = df.rename(columns=cov_rename)

    # Drop non-item, non-covariate columns
    # pid = UUID string identifier (not used), know1-6 are political knowledge items
    # group22-25 are feeling thermometers (1-8 scale, different from policy items)
    # We focus on the 4 core policy reform items: certif, carotid, review, interv
    # Per the paper these are the primary outcome measures (support for police reforms, 1-5)
    item_cols = ["certif", "carotid", "review", "interv"]
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    long = df[["id", "treat"] + cov_cols + item_cols].melt(
        id_vars=["id", "treat"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )

    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # Filter to valid scale range (1-5)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    # Enforce column order: id, item, resp, treat, cov_*
    long = long[["id", "item", "resp", "treat"] + cov_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_name = "boudreau_2022_police_reform"
    out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(out_path, index=False)
    print(
        f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
    )


if __name__ == "__main__":
    convert()
