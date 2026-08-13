#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6087617
# DOI: 10.7717/peerj.5425
#
# Gobbens (2018), "Associations of ADL and IADL disability with physical
# and mental dimensions of quality of life in people aged 75 years and
# older." PeerJ. CC BY 4.0. N=377.
# Supplementary file peerj-06-5425-s001.sav has three raw-item scales:
# an 11-item ADL (Katz-style) disability questionnaire (1-4, "fully
# independent without difficulty" to "cannot do independently"), a 7-item
# IADL disability questionnaire (same 1-4 response format), and the
# 12-item SF-12 health survey (mixed per-item response formats: 2-,3-,5-,
# and 6-point items, standard for SF-12). *disability/*dimension/SF12
# subdomain columns are pre-computed aggregates, excluded per
# datastandard.md. No person ID column in the source file; row index used.

import io
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6087617/supplementaryFiles"
MEMBER = "peerj-06-5425-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ADL_COLS = [f"ADL{i}" for i in range(1, 12)]
IADL_COLS = [f"IADL{i}" for i in range(1, 8)]
SF12_COLS = ["SF12_1", "SF12_2", "SF12_2b", "SF12_3A", "SF12_3B", "SF12_4A",
             "SF12_4B", "SF12_5", "SF12_6A", "SF12_6B", "SF12_6C", "SF12_7"]

COV_RENAME = {
    "Ageinyears": "cov_age",
    "SexR": "cov_sex",
    "MaritalstatusR": "cov_marital_status",
    "Education": "cov_education",
    "Income": "cov_income",
    "MultimorbidityR": "cov_multimorbidity",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        df, _meta = pyreadstat.read_sav(io.BytesIO(f.read()))
    return df


def build_scale(df: pd.DataFrame, cols: list[str], out_name: str):
    d = df.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    cov_cols = list(COV_RENAME.values())
    keep = d[["id"] + cols + list(COV_RENAME.keys())].rename(columns=COV_RENAME)

    long = keep.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    raw = fetch_raw()
    assert raw["Ageinyears"].min() >= 75
    build_scale(raw, ADL_COLS, "gobbens_2018_adl.csv")
    build_scale(raw, IADL_COLS, "gobbens_2018_iadl.csv")
    build_scale(raw, SF12_COLS, "gobbens_2018_sf12.csv")


if __name__ == "__main__":
    convert()
