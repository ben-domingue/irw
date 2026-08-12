#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC4671186 (PeerJ)
# DOI: 10.7717/peerj.1464
# License: CC BY 4.0
#
# "The association of parental temperament and character on their
# children's behavior problems" (Lee, 2015, PeerJ). Raw file
# (peerj-03-1464-s001.xlsx) bundles the 100-item Korean CBCL (Child
# Behavior Checklist, 0/1/2 scale) alongside a large multi-informant
# Junior Temperament and Character Inventory (JTCI) battery -- child-,
# mother-, and father-report versions of the same 7 subscales, each with
# raw items plus subscale-sum and percentile-transformed columns
# (i/m/p-prefixed: iNS1-4/iNS/iNS100, etc.) and several Korean-language
# CBCL composite-subscale columns. Only the CBCL raw items are shipped
# here -- the JTCI multi-informant block is real, recoverable item data
# but was not disentangled in this pass (needs the paper's Methods text
# to confirm which subscale abbreviations map to which JTCI dimension per
# informant); flagged in BATCH_LOG.md as still-open follow-up work.

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4671186/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = [f"CBCL_{i:02d}" for i in range(1, 101)]
COV_MAP = {"ID": "id", "sex": "cov_sex", "age_months": "cov_age_months"}


def _fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPP_URL, headers=UA, timeout=60)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    xlsx_name = [n for n in zf.namelist() if n.endswith("s001.xlsx")][0]
    return pd.read_excel(io.BytesIO(zf.read(xlsx_name)))


def convert():
    df = _fetch_raw()
    df = df.rename(columns=COV_MAP)
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df = df.drop_duplicates(subset=["id"], keep="first")
    cov_cols = ["cov_sex", "cov_age_months"]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.lower()
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 2)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "lee_2015_cbcl"
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
