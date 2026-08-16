#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6511389
# DOI: 10.7717/peerj.6254
#
# Matranga & Lumia (2019), "The vaccinaTion & Hpv Knowledge (THinK)
# questionnaire: a reliability and validity study on a sample of women
# living in Sicily (southern-Italy)." PeerJ. CC BY 4.0. N=220.
#
# Single supplementary file (peerj-07-6254-s001.xlsx) holds raw responses
# to all 16 THinK items (5-level Likert per the paper's Methods section:
# yes-much/somewhat/little/no, recorded here as integer codes 1-6) plus
# demographic covariates. Raw `ID ` column (note trailing space in source
# header) is unique per respondent and used as `id`. `Age` has a literal
# "." sentinel for missing -- coerced to NaN via pd.to_numeric.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6511389/supplementaryFiles"
DATA_FILE_IN_ZIP = "peerj-07-6254-s001.xlsx"

ITEM_COLS = [f"Q{i}" for i in range(1, 17)]

COV_COLS = {
    "Group": "cov_recruitment_group",   # O=Ob/Gyn dept, A=University Ambulatory Clinic
    "Age": "cov_age",
    "Education": "cov_education",
    "Place of birth": "cov_place_of_birth",
    "Place of living": "cov_place_of_living",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPP_URL, timeout=60)
    r.raise_for_status()
    import zipfile

    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        with zf.open(DATA_FILE_IN_ZIP) as f:
            df = pd.read_excel(f)
    df = df.rename(columns={"ID ": "id"})
    return df


def convert():
    print("Downloading THinK supplementary data …")
    raw = fetch_raw()

    raw["cov_age"] = pd.to_numeric(raw["Age"], errors="coerce")
    for src, cov in COV_COLS.items():
        if cov == "cov_age":
            continue
        raw[cov] = raw[src]

    cov_names = list(COV_COLS.values())
    long = raw[["id"] + ITEM_COLS + cov_names].melt(
        id_vars=["id"] + cov_names,
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["item"] = long["item"].str.lower()
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    col_order = ["id", "item", "resp"] + cov_names
    long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "matranga_2019_hpv_knowledge.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")


if __name__ == "__main__":
    convert()
