#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11809301
# DOI: 10.7717/peerj.18809
#
# Galgam et al. (2025), "Assessing the quality of life among African
# medical and health science students using the WHOQOL-BREF tool." PeerJ.
# CC BY 4.0 (confirmed via full-text XML <license-p>: "Creative Commons
# Attribution License"). N=349. 26-item WHOQOL-BREF, 5-category text
# Likert with 4 different response-category wordings across items (the
# supplementary "Code" sheet documents these; item 1/15 use a poor-good
# scale, item 2/16-25 use a satisfaction scale, items 3-14 use an
# amount/degree scale, item 26 uses a frequency scale). Items 3-26 all
# carry a leading digit in their text label ("3. A moderate amount") that
# is extracted directly; items 1-2 have no leading digit and are mapped
# explicitly from the codebook. Response direction is consistent within
# each item (1=worst..5=best framing throughout), matching
# datastandard.md's per-item (not cross-item) direction requirement.
# No PII in any column (Gender/Nationality/Age Group/Marital
# Status/Faculty/Year are ordinary demographic covariates).

import io
import re
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11809301/supplementaryFiles"
MEMBER = "peerj-13-18809-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

Q1_MAP = {
    "very poor": 1, "poor": 2, "neither poor nor good": 3,
    "good": 4, "very good": 5,
}
Q2_MAP = {
    "very dissatisfied": 1, "dissatisfied": 2,
    "neither satisfied nor dissatisfied": 3,
    "satisfied": 4, "very satisfied": 5,
}

COV_RENAME = {
    "Gender": "cov_gender",
    "Nationality": "cov_nationality",
    "Age": "cov_age_group",
    "Marital Status": "cov_marital_status",
    "Your Faculty": "cov_faculty",
    "Year / Level": "cov_year",
}


def _norm_q2(s):
    s = s.strip().lower()
    has_very = "very" in s
    has_dis = "dissatisfied" in s
    has_neither = "neither" in s
    if has_neither:
        return 3
    if has_dis and has_very:
        return 1
    if has_dis and not has_very:
        return 2
    if has_very and not has_dis:
        return 5
    return 4  # bare "satisfied"


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)), sheet_name="Sheet1")

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    item_cols = [c for c in df.columns if c not in cov_cols]
    assert len(item_cols) == 26, f"expected 26 items, got {len(item_cols)}"

    item_names = [f"item_{i}" for i in range(1, 27)]
    rename_items = dict(zip(item_cols, item_names))
    df = df.rename(columns=rename_items)

    df["item_1"] = df["item_1"].astype(str).str.strip().str.lower().map(Q1_MAP)
    df["item_2"] = df["item_2"].astype(str).str.strip().apply(_norm_q2)
    for i in range(3, 27):
        col = f"item_{i}"
        extracted = df[col].astype(str).str.strip().str.extract(r"^(\d+)")[0]
        df[col] = pd.to_numeric(extracted, errors="coerce")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_names,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_path = OUT_DIR / "galgam_2025_whoqol_bref.csv"
    long.to_csv(out_path, index=False)
    print(f"galgam_2025_whoqol_bref: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
