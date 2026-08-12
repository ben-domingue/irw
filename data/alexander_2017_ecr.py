#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC5345385 (PeerJ)
# DOI: 10.7717/peerj.3034
# License: CC BY 4.0
#
# Companion file to alexander_2017_dsi.py -- see that script's header for
# the source/cleanup explanation (junk annotation rows dropped by
# coercing to numeric; non-unique 'Subject code' replaced with the row
# index as `id`). This file ships the Experiences in Close Relationships
# (ECR) attachment scale, 36 items, 1-7 scale -- the instrument most
# directly tied to the paper's "attachment anxiety" framing.

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5345385/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ECR_ITEMS = [f"ECR {i}" for i in range(1, 37)]


def _fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPP_URL, headers=UA, timeout=60)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    xlsx_name = [n for n in zf.namelist() if n.endswith("s001.xlsx")][0]
    return pd.read_excel(io.BytesIO(zf.read(xlsx_name)))


def convert():
    df = _fetch_raw()
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    long = df.melt(id_vars=["id"], value_vars=ECR_ITEMS,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("ECR ", "ecr_", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "alexander_2017_ecr"
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
