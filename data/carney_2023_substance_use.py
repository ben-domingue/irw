#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0290781
# DOI: 10.1371/journal.pone.0290781
# Carney et al. (2023), "Latent class analysis of substance use typologies
# associated with mental and sexual health outcomes among sexual and gender
# minority youth", PLOS ONE. CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0290781.s001

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0290781.s001"

ITEM_COLS = ["alcohol", "stimulant", "sedatives", "opioid", "club drugs",
             "cannabis", "amylnitrite ", "hallucinogen"]
COV_RENAME = {
    "age_raw": "cov_age",
    "education_cat ": "cov_education",
    "housing_d": "cov_housing",
    "cismen": "cov_cismen",
    "trans": "cov_trans",
    "nonbinary": "cov_nonbinary",
    "gay": "cov_gay",
    "bisexual": "cov_bisexual",
    "hispanic": "cov_hispanic",
    "race_white": "cov_race_white",
    "race_black ": "cov_race_black",
    "race_other": "cov_race_other",
    "race_mixed": "cov_race_mixed",
}
COV_COLS = list(COV_RENAME.values())


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"id": "id", **COV_RENAME})
    df = df.rename(columns={c: c.strip() for c in ITEM_COLS})
    item_cols = [c.strip() for c in ITEM_COLS]

    long = df.melt(id_vars=["id"] + COV_COLS, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + COV_COLS]

    path = os.path.join(OUT_DIR, "carney_2023_substance_use.csv")
    long.to_csv(path, index=False)
    print(f"carney_2023_substance_use: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
