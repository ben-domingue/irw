#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11670754 (PeerJ)
# DOI: 10.7717/peerj.18709
# License: CC BY 4.0
#
# "Quality of life and subjective well-being comparison between traumatic,
# nontraumatic chronic spinal cord injury, and healthy individuals in
# China" (Altahla et al., 2024, PeerJ). Supplementary file
# peerj-12-18709-s001.xlsx has 4 sheets: 'Sheet1' (n=189, spinal-cord-
# injury sample), 'GP' (n=223, healthy general-population comparison
# sample), and 'participants test' / 're test' (a 30-person test-retest
# reliability subsample with its own 1-30 id numbering that cannot be
# reliably linked back to Sheet1's ids -- skipped, not shipped).
#
# Columns 1-26 are the WHOQOL-BREF (WHO Quality of Life, brief version),
# a standard 26-item instrument on a 1-5 scale -- shipped here. Columns
# 27-31 are the 5-item Satisfaction With Life Scale (SWLS, 1-7 scale) --
# a separate instrument, shipped as its own file
# (altahla_2024_swls.py) per the one-scale-per-file rule.
#
# Sheet1 and GP are combined into one file with cov_group distinguishing
# SCI patients from healthy controls -- both used the identical WHOQOL-BREF
# item set (confirmed by identical column text). GP's ids (1-223) are
# offset by +100000 to avoid colliding with Sheet1's ids (1-189), per
# datastandard.md's same-instrument/multiple-samples guidance. Sheet1-only
# injury/demographic covariates (columns 32-44) are NaN for the GP rows,
# since the general-population sample was never asked those questions.

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11670754/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

WHOQOL_ITEMS = [f"whoqol_{i}" for i in range(1, 27)]
SWLS_ITEMS = [f"swls_{i}" for i in range(1, 6)]

SCI_COV_NAMES = [
    "cov_gender", "cov_married", "cov_age", "cov_education", "cov_employee",
    "cov_injury_duration", "cov_age_at_injury", "cov_injury_type",
    "cov_injury_severity", "cov_injury_level", "cov_paralysis_type",
    "cov_injury_cause", "cov_injury_state",
]
ALL_COV_COLS = ["cov_group"] + SCI_COV_NAMES


def _fetch_workbook() -> pd.ExcelFile:
    r = requests.get(SUPP_URL, headers=UA, timeout=60)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    xlsx_name = [n for n in zf.namelist() if n.endswith("s001.xlsx")][0]
    return pd.ExcelFile(io.BytesIO(zf.read(xlsx_name)))


def _load_sheet1(xls: pd.ExcelFile) -> pd.DataFrame:
    df = pd.read_excel(xls, "Sheet1")
    df.columns = ["id"] + WHOQOL_ITEMS + SWLS_ITEMS + SCI_COV_NAMES
    assert df["id"].nunique() == len(df), "Sheet1 id not unique"
    df["cov_group"] = "sci"
    return df


def _load_gp(xls: pd.ExcelFile) -> pd.DataFrame:
    df = pd.read_excel(xls, "GP")
    df.columns = ["id"] + WHOQOL_ITEMS + SWLS_ITEMS
    assert df["id"].nunique() == len(df), "GP id not unique"
    df["id"] = df["id"] + 100000  # offset to avoid colliding with Sheet1
    df["cov_group"] = "healthy"
    for c in SCI_COV_NAMES:
        df[c] = pd.NA
    return df


def _melt_scale(df: pd.DataFrame, item_cols: list[str], valid_max: float) -> pd.DataFrame:
    long = df.melt(id_vars=["id"] + ALL_COV_COLS, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= valid_max)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"] + ALL_COV_COLS]


def convert():
    xls = _fetch_workbook()
    combined = pd.concat([_load_sheet1(xls), _load_gp(xls)], ignore_index=True)

    long = _melt_scale(combined, WHOQOL_ITEMS, valid_max=5)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "altahla_2024_whoqol"
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
