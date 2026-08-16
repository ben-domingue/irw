#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC12617366
# DOI: 10.7717/peerj.20310
#
# Sinsopa & Tripakornkusol (2025), "Modified STOP-Bang questionnaire for
# detecting obstructive sleep apnea in individuals with a body mass index
# below 35 kg/m2." PeerJ. CC BY 4.0. N=188.
#
# The raw file mixes the 8 binary STOP-Bang screening items with
# continuous anthropometric covariates (height/weight/bmi/neck
# circumference/age) and composite outputs (Original/New STOPBang score,
# apnea-hypopnea index, severity, OSA diagnosis) -- only the 8 binary
# item columns are used as `resp`; everything else is either a covariate
# input to those items or a derived composite and is dropped.
# `bmi35` is constant (all 0 in this sample -- by inclusion criteria,
# BMI<35) and is dropped as a zero-variance item.

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12617366/supplementaryFiles"
DATA_FILE_IN_ZIP = "peerj-13-20310-s001.xlsx"

ITEM_COLS = {
    "snoring 1 yes": "snoring",
    "tired 1 yes": "tired",
    "observed apnea 1 yes": "observed_apnea",
    "hypertension 1 yes": "hypertension",
    "age50": "age_ge_50",
    "neck40": "neck_ge_40cm",
    "sex 1 male": "male",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPP_URL, timeout=60)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        with zf.open(DATA_FILE_IN_ZIP) as f:
            df = pd.read_excel(f)
    return df.rename(columns={"record_id": "id"})


def convert():
    print("Downloading modified STOP-Bang supplementary data …")
    raw = fetch_raw()

    src_cols = list(ITEM_COLS.keys())
    long = raw[["id"] + src_cols].melt(
        id_vars=["id"], value_vars=src_cols, var_name="item", value_name="resp"
    )
    long["item"] = long["item"].map(ITEM_COLS)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "sinsopa_2025_stopbang.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")


if __name__ == "__main__":
    convert()
