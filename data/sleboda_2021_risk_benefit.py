#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255569
# DOI: 10.1371/journal.pone.0255569
# Supporting Information: https://doi.org/10.1371/journal.pone.0255569.s001
#
# 80-item risk/benefit-perception battery: 5 hazard domains (genetic
# testing GT, stem-cell research SC, pesticides PE, energy/nuclear EN,
# vaccination VA) each rated on 16 semantic-differential dimensions
# (dread, novelty, voluntariness of exposure, etc.), 11-point scale.
# pd.read_spss's default value-label handling mixes numeric and labeled-
# endpoint strings inconsistently across these columns (labels exist only
# at the scale's endpoints) -- convert_categoricals=False is required to
# get clean 1-11 codes throughout. AT_*, NFC, dis_*_h/e, and
# NFC_SD_classification columns are derived composites/attitude indices,
# not raw items, and are dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0255569.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Gender": "cov_gender", "Education": "cov_education",
              "Income": "cov_income", "Age": "cov_age", "Location": "cov_location"}

DOMAIN_PREFIXES = ["GT_", "SC_", "PE_", "EN_", "VA_"]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content), convert_categoricals=False)

    df = df.rename(columns={"ID": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    item_cols = [c for c in df.columns if any(c.startswith(p) for p in DOMAIN_PREFIXES)]
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 11)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "sleboda_2021_risk_benefit.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
