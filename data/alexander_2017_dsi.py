#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC5345385 (PeerJ)
# DOI: 10.7717/peerj.3034
# License: CC BY 4.0
#
# "Attachment anxiety is associated with a fear of becoming fat, which is
# mediated by binge eating" (Alexander, 2017, PeerJ). The raw supplementary
# file (peerj-05-3034-s001.xlsx) bundles 6 instruments (DSI, ECR, PA, EAS,
# Binge EA, Anti-fat) plus several stray annotation/legend rows mixed into
# the data (e.g. a cell literally reading "*Differentiation of self(DSI)")
# -- these are dropped by coercing every item column to numeric and
# requiring the row to have at least one valid item response. 'Subject
# code' is a non-unique string (148 unique for 172 rows, partly due to the
# junk rows) -- the row index is used as `id` instead per datastandard.md.
#
# This file ships only the Differentiation of Self Inventory (DSI, 23
# items, 1-6 scale) -- one of the instruments most directly tied to the
# paper's title. See alexander_2017_ecr.py for the companion Experiences
# in Close Relationships (attachment) scale from the same file. The
# remaining instruments (PA, EAS, Binge EA, Anti-fat) were not processed
# in this pass -- flagged in BATCH_LOG.md as still-open follow-up work.

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

DSI_ITEMS = [f"DSI {i}" for i in range(1, 24)]


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

    long = df.melt(id_vars=["id"], value_vars=DSI_ITEMS,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("DSI ", "dsi_", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 6)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "alexander_2017_dsi"
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
