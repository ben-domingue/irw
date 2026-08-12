#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13048223
# DOI: 10.7717/peerj.20868
#
# Han et al. (2026), "Network analysis of anxiety, depression and
# insomnia in the elderly in Jiangsu Province." PeerJ. CC BY 4.0. N=2086.
# PHQ-9 (depression) file -- see han_2026_gad7.py for the shared-source
# note (peerj-14-20868-s006.xlsx, one paper split into 3 IRW files).
# Standard 0-3 frequency scale; PHQ_Score is the pre-computed subscale
# total, excluded as an aggregate per datastandard.md.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13048223/supplementaryFiles"
MEMBER = "peerj-14-20868-s006.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PHQ_ITEMS = [f"PHQ0{i}" for i in range(1, 10)]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))
    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"], value_vars=PHQ_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "han_2026_phq9.csv"
    long.to_csv(out_path, index=False)
    print(f"han_2026_phq9: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
