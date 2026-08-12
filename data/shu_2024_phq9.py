#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11488497
# DOI: 10.7717/peerj.18225
#
# Shu et al. (2024), "The effects of subjective family status and
# subjective school status on depression and suicidal ideation among
# adolescents." PeerJ. CC BY 4.0. N=1190. Raw PHQ-9 items (text-coded
# 4-point frequency scale, recoded 0-3 in category order); PHQtotal is
# the pre-computed subscale total, excluded as an aggregate. A couple of
# categories have trailing-period typos ("Not at all.") normalized before
# mapping. GAD-7 items from the same file are shipped separately as
# shu_2024_gad7.py per datastandard.md's "one file per scale" rule.

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11488497/supplementaryFiles"
MEMBER = "peerj-12-18225-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PHQ_ITEMS = [f"PHQ{i}" for i in range(1, 10)]
LIKERT_MAP = {
    "not at all": 0,
    "a couple of days": 1,
    "more than half the time": 2,
    "almost every day": 3,
}


def _clean(s):
    return s.astype(str).str.strip().str.rstrip(".").str.lower().map(LIKERT_MAP)


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(zf.read(MEMBER))
        tmp.flush()
        df = pd.read_spss(tmp.name)
    df = df.rename(columns={"number": "id"})
    assert df["id"].nunique() == len(df)

    for c in PHQ_ITEMS:
        df[c] = _clean(df[c])

    long = df.melt(id_vars=["id"], value_vars=PHQ_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "shu_2024_phq9.csv"
    long.to_csv(out_path, index=False)
    print(f"shu_2024_phq9: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
