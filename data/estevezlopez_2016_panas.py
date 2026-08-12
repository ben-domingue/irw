#!/usr/bin/env python3
# Source: https://peerj.com/articles/1822/ (PMC4817417)
# DOI: 10.7717/peerj.1822
#
# Estevez-Lopez et al. (2016), "Factor structure of the Positive and
# Negative Affect Schedule (PANAS) in adult women with fibromyalgia from
# Southern Spain: the al-Andalus project." CC BY 4.0. N=442. Standard
# 20-item PANAS, 5-point Likert (1-5). Found via irw_discover_pmc.py
# (Europe PMC "PANAS" query against PeerJ); supplementary file fetched
# through Europe PMC's supplementaryFiles endpoint (PMC4817417).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

OUT_NAME = "estevezlopez_2016_panas"
SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4817417/supplementaryFiles"
MEMBER = "peerj-04-1822-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Source columns are "1st_item".."20th_item" -- positional, not otherwise
# meaningful -- renamed to a scale-specific sequential label.
ITEM_COLS = [f"{n}{s}_item" for n, s in [
    (1, "st"), (2, "nd"), (3, "rd")] + [(i, "th") for i in range(4, 21)]]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))

    df = df.rename(columns={"Participant": "id"})
    rename_items = {c: f"panas_{i+1}" for i, c in enumerate(ITEM_COLS)}
    df = df.rename(columns=rename_items)
    item_cols = list(rename_items.values())

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / f"{OUT_NAME}.csv"
    long.to_csv(out_path, index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
