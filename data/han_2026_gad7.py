#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13048223
# DOI: 10.7717/peerj.20868
#
# Han et al. (2026), "Network analysis of anxiety, depression and
# insomnia in the elderly in Jiangsu Province." PeerJ. CC BY 4.0. N=2086.
# Supplementary file peerj-14-20868-s006.xlsx bundles three raw-item
# instruments (GAD-7, PHQ-9, ISI-7) plus their pre-computed *_Score totals
# and demographics -- each instrument is split into its own IRW file per
# datastandard.md's "one file per scale" rule. This script produces the
# GAD-7 (anxiety) file; see han_2026_phq9.py and han_2026_isi.py for the
# other two. (Two other SI files, s001.xlsx/s002.xlsx, hold an earlier/
# alternate insomnia+depression item set with messier encoding -- not
# used; s006.xlsx is the clean, complete, codebook-matching source.)
# GAD-7 items are the standard 0-3 frequency scale ("not at all" to
# "nearly every day"); *_Score columns are pre-computed subscale totals,
# excluded as aggregates per datastandard.md.

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

GAD_ITEMS = [f"GAD0{i}" for i in range(1, 8)]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))
    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"], value_vars=GAD_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "han_2026_gad7.csv"
    long.to_csv(out_path, index=False)
    print(f"han_2026_gad7: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
