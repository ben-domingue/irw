#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11967409
# DOI: 10.7717/peerj.19127
#
# Ajlan & Ashri (2025), "Knowledge and attitude of dental school faculties
# towards stem cell therapies and their applications." PeerJ. CC BY 4.0.
# N=101 (one duplicate `Fsno` value out of 102 rows dropped as a
# data-entry duplicate).
#
# The raw .sav file gives each Likert/yes-no item twice: once as a
# human-readable text category (e.g. "Agree"/"Strongly agree") and once
# as an "a"-suffixed numeric recode of the same column (e.g. `Q11.1` vs
# `Q11.1a`) -- the numeric "a" columns are used directly as `resp`.
# Response scales differ by item (3-level yes/no/not-sure items vs.
# 4-level agree/disagree items), which is expected for this instrument
# and left as-is per item.

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11967409/supplementaryFiles"
DATA_FILE_IN_ZIP = "peerj-13-19127-s004.sav"

ITEM_COLS = [
    "Q11.1a", "Q11.2a", "Q11.3a",
    "Q14.1a", "Q14.2a", "Q14.3a", "Q14.4a", "Q14.5a", "Q14.6a",
    "Q14.7a", "Q14.8a", "Q14.9a",
    "Q15a", "Q16a", "Q17a", "Q18a", "Q19a", "Q20a", "Q21a",
    "Q22.1a", "Q22.2a", "Q22.3a", "Q22.4a", "Q22.5a", "Q22.6a",
    "Q23.1a", "Q23.2a", "Q23.3a", "Q23.4a", "Q23.5a",
]

COV_COLS = {
    "Q1_Age": "cov_age_bracket",
    "Q2_Gender": "cov_gender",
    "Q3_Nationality": "cov_nationality",
    "Q4_Speciality": "cov_speciality",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPP_URL, timeout=60)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        with zf.open(DATA_FILE_IN_ZIP) as f:
            df = pd.read_spss(io.BytesIO(f.read()))
    return df


def convert():
    print("Downloading stem cell knowledge/attitude supplementary data …")
    raw = fetch_raw()

    raw = raw.rename(columns={"Fsno": "id"})
    raw = raw.drop_duplicates(subset="id", keep="first").reset_index(drop=True)

    for src, cov in COV_COLS.items():
        raw[cov] = raw[src]

    cov_names = list(COV_COLS.values())
    long = raw[["id"] + ITEM_COLS + cov_names].melt(
        id_vars=["id"] + cov_names,
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["item"] = (
        long["item"].str.replace("a$", "", regex=True)
        .str.replace(".", "_", regex=False)
        .str.lower()
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    col_order = ["id", "item", "resp"] + cov_names
    long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "ajlan_2025_stemcell_knowledge.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")


if __name__ == "__main__":
    convert()
