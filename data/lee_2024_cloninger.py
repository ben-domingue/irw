#!/usr/bin/env python3
# Source: https://peerj.com/articles/18379/ (PMC11566513)
# DOI: 10.7717/peerj.18379
#
# Lee et al. (2024), "The associations between well-being and Cloninger's
# personality dimensions in a Korean community sample." PeerJ. CC BY 4.0.
# N=527. Found via irw_discover_pmc.py (Europe PMC "Satisfaction with Life
# Scale" query against PeerJ).
#
# QC note: the single supplementary file bundles FOUR distinct instruments
# in one sheet -- split here into 4 IRW files per datastandard.md's
# one-scale-per-file rule, rather than shipped as one 193-item table (what
# irw_discover_pmc.py's auto-triage originally flagged "good" on):
#   - Cloninger's Temperament and Character Inventory (i1-i140, 0-4 scale)
#   - Satisfaction with Life Scale (SWLS1-5, 1-7 scale)
#   - PANAS (PANAS1-20, 1-5 scale)
#   - a Social Support scale (Social Support_01-25, 1-5 scale)
# A single "Subjective health" item and age/sex are carried as covariates
# on every file rather than shipped as their own 1-item table (never ship
# a table with only 1 distinct item).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11566513/supplementaryFiles"
MEMBER = "peerj-12-18379-s002.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "age": "cov_age",
    "sex": "cov_gender",
    "Subjective health": "cov_subjective_health",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    cov_cols = list(COV_RENAME.values())

    scales = {
        "lee_2024_tci": [c for c in df.columns if c.startswith("i") and c[1:].isdigit()],
        "lee_2024_swls": [c for c in df.columns if c.startswith("SWLS")],
        "lee_2024_panas": [c for c in df.columns if c.startswith("PANAS")],
        "lee_2024_social_support": [c for c in df.columns if c.startswith("Social Support")],
    }

    for out_name, item_cols in scales.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
