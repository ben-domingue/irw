#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13048223
# DOI: 10.7717/peerj.20868
#
# Han et al. (2026), "Network analysis of anxiety, depression and
# insomnia in the elderly in Jiangsu Province." PeerJ. CC BY 4.0. N=2086.
# Insomnia Severity Index (ISI-7) file -- see han_2026_gad7.py for the
# shared-source note (peerj-14-20868-s006.xlsx, one paper split into 3
# IRW files). Each item is internally a consistent 5-point ordinal scale;
# raw codes vary by item (some 0-4, some 1-5) which datastandard.md
# permits ("direction may vary across items" -- range does too, as long
# as each item is internally consistent, which was checked here).
# ISI_Score is the pre-computed subscale total, excluded as an aggregate.

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

ISI_ITEMS = [f"ISI0{i}" for i in range(1, 8)]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))
    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"], value_vars=ISI_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "han_2026_isi.csv"
    long.to_csv(out_path, index=False)
    print(f"han_2026_isi: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
