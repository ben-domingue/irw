#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9575671
# DOI: 10.7717/peerj.14240
#
# Almuqbil et al. (2022), "Postpartum depression and health-related
# quality of life: a Saudi Arabian perspective." PeerJ. CC BY 4.0. N=253.
# Supplementary file peerj-10-14240-s001.xlsx bundles a 10-item Edinburgh
# Postnatal Depression Scale (EPDS, 0-3 per item) with SUM/
# Depression-categorical/depression-Numerical aggregates (excluded per
# datastandard.md) and an SF-12 block. The SF-12 columns in this file are
# free-text response categories with many rows holding concatenated
# multi-answer strings (e.g. "Most of the time,  A good bit of the
# time") rather than a single clean category -- not reliably parseable
# into an ordinal code without guessing, so only the clean numeric EPDS
# scale is shipped here; the SF-12 block is left out. No PII in the
# source file (age/nationality/marital status only, no names).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9575671/supplementaryFiles"
MEMBER = "peerj-10-14240-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

EPDS_COLS = [
    "I have been able to laugh and see the funny side of things I have felt happy",
    "I have looked forward with enjoyment to things",
    ". I have blamed myself unnecessarily when things went wrong",
    "I have been anxious or worried for no good reason",
    "I have felt scared or panicky for no very good reason",
    "Things have been getting on top of me",
    "I have been so unhappy that I have had difficulty sleeping",
    ". I have felt sad or miserable:",
    "I have been so unhappy that I have been crying:",
    "The thought of harming myself has occurred to me",
]
EPDS_ITEM_NAMES = [f"epds_{i}" for i in range(1, 11)]

COV_RENAME = {
    "Age": "cov_age",
    "Marital status": "cov_marital_status",
    "Educational level": "cov_education",
    "Employment status": "cov_employment",
    "Nationality": "cov_nationality",
}


def convert():
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    keep = df[["id"] + EPDS_COLS + cov_cols].copy()
    keep.columns = ["id"] + EPDS_ITEM_NAMES + cov_cols

    long = keep.melt(id_vars=["id"] + cov_cols, value_vars=EPDS_ITEM_NAMES,
                      var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "almuqbil_2022_epds.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
