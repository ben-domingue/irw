#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0284335
# DOI: 10.1371/journal.pone.0284335
# Supporting Information: https://doi.org/10.1371/journal.pone.0284335.s007
#
# Raw file bundles 3 distinct scales -- Rosenberg Self-Esteem (10 items),
# Second Language Writing Anxiety Inventory (22 items), Mobile Phone
# Addiction Tendency Scale (16 items) -- administered to Chinese medical
# students. One output file per scale.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0284335.s007")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "GENDER": "cov_gender",
    "AGE": "cov_age",
    "GRADE": "cov_grade",
    "MAJOR": "cov_major",
    "INCOME": "cov_family_income",
    "DADEDU": "cov_father_education",
    "MOMEDU": "cov_mother_education",
    "FAMILYLOCATION": "cov_family_location",
    "MEDICALHISTORY": "cov_medical_history",
}

SCALES = {
    "song_2023_rses": [f"RSES{i}" for i in range(1, 11)],
    "song_2023_slwai": [f"SLWAI{i}" for i in range(1, 23)],
    "song_2023_mpats": [f"MPATS{i}" for i in range(1, 17)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)


if __name__ == "__main__":
    convert()
