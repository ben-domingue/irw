#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10655721
# DOI: 10.7717/peerj.16375
#
# "Psychometric properties of the Mexican version of the Opening Minds
# Stigma Scale for health care providers." PeerJ. CC BY 4.0. N=556.
# 15-item OMS-HC scale, 5-category text Likert ("completely disagree" to
# "completely agree"), recoded 1-5 in category order. No person-ID column
# in the raw .sav file -- row index used per datastandard.md. `Total` is
# the paper's pre-computed (partially reverse-scored) sum, excluded as an
# aggregate; this file ships raw per-item responses, not the composite.

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10655721/supplementaryFiles"
MEMBER = "peerj-11-16375-s003.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = [f"oms{i}" for i in range(1, 16)]
LIKERT_MAP = {
    "completely disagree": 1,
    "disagree": 2,
    "neither agree nor disagree": 3,
    "agree": 4,
    "completely agree": 5,
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(zf.read(MEMBER))
        tmp.flush()
        df = pd.read_spss(tmp.name)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    for c in ITEMS:
        df[c] = df[c].astype(str).str.strip().map(LIKERT_MAP)

    long = df.melt(id_vars=["id"], value_vars=ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "valdivia_2023_oms.csv"
    long.to_csv(out_path, index=False)
    print(f"valdivia_2023_oms: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
