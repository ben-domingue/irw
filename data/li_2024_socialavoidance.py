#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11332389 (PeerJ)
# DOI: 10.7717/peerj.17910
# License: CC BY 4.0
#
# "Does how individuals handle social situations exacerbate the
# relationship between physique anxiety and food addiction?" (Li, 2024,
# PeerJ). Raw file (peerj-12-17910-s001.xlsx) bundles 4 instruments:
# FA (Food Addiction, 13 binary items), BDYZ (a 4-item subset of a body-
# image scale -- only items 1/2/6/9 are present in the raw file, not a
# truncation error on our end), SPA (Social Physique Anxiety, 15 items,
# 1-5), SAD (Social Avoidance and Distress, 28 binary items). Three
# derived columns ("ditress of FA", "Elevenitems1", "FA ") are excluded
# as composite/derived scores, not raw items.

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11332389/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "Number": "id", "Gender": "cov_gender", "HomeLocation": "cov_home_location",
    "Smoking Per Day": "cov_smoking_per_day", "Age": "cov_age", "Height": "cov_height",
    "Weight": "cov_weight", "Bed Time": "cov_bed_time", "Education": "cov_education",
}
COV_COLS = list(COV_MAP.values())[1:]

SCALES = {
    "fa": ([f"FA{i}" for i in range(1, 14)], 0, 1),
    "bdyz": (["BDYZ1", "BDYZ2", "BDYZ6", "BDYZ9"], 1, 7),
    "spa": ([f"SPA{i}" for i in range(1, 16)], 1, 5),
    "sad": ([f"SAD{i}" for i in range(1, 29)], 0, 1),
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

        out_name = f"li_2024_{scale}"
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
