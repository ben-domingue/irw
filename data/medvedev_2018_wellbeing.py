#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC5985772 (PeerJ)
# DOI: 10.7717/peerj.4903
# License: CC BY 4.0
#
# "Exploring constructs of well-being, happiness and quality of life"
# (Medvedev, 2018, PeerJ). Raw file (peerj-06-4903-s001.xlsx) bundles 4
# instruments: OXH (Oxford Happiness Questionnaire, 29 items, 1-6),
# QL (quality-of-life scale, 26 items, 1-5), SL (Satisfaction With Life
# Scale, 5 items, 1-7), PAN (PANAS, 20 items, 1-5). Each item also has a
# reverse-scored duplicate column (e.g. OXH1R = 7-OXH1) used only for the
# paper's own composite-scoring -- these *R columns, plus the derived
# composite/subscale-total columns (OXHTOTAL, QLSOCIAL, QLPHYCH, QLENV,
# QLPHYSICAL, SLTOTAL, PANPOS, PANNEG, PANNEGR), are excluded here. Only
# the as-recorded raw item responses are shipped, per datastandard.md's
# resp_direction guidance -- not the analysis-convenience reverse-coded
# duplicates.

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5985772/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"CASES": "id", "GENDER": "cov_gender", "AGE": "cov_age", "ETHNIC": "cov_ethnicity"}
COV_COLS = ["cov_gender", "cov_age", "cov_ethnicity"]

SCALES = {
    "oxh": ([f"OXH{i}" for i in range(1, 30)], 1, 6),
    "ql": ([f"QL{i}" for i in range(1, 27)], 1, 5),
    "sl": ([f"SL{i}" for i in range(1, 6)], 1, 7),
    "pan": ([f"PAN{i}" for i in range(1, 21)], 1, 5),
}


def _fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPP_URL, headers=UA, timeout=60)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    xlsx_name = [n for n in zf.namelist() if n.endswith("s001.xlsx")][0]
    return pd.read_excel(io.BytesIO(zf.read(xlsx_name)))


def convert():
    df = _fetch_raw()
    df = df.rename(columns=COV_MAP)
    assert df["id"].nunique() == len(df), "id not unique"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for scale, (items, lo, hi) in SCALES.items():
        long = df.melt(id_vars=["id"] + COV_COLS, value_vars=items,
                        var_name="item", value_name="resp")
        long["item"] = scale + "_" + long["item"].str.extract(r"(\d+)$")[0]
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + COV_COLS]

        out_name = f"medvedev_2018_{scale}"
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
