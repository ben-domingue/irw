#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0246875
# DOI: 10.1371/journal.pone.0246875
# Supporting Information: https://doi.org/10.1371/journal.pone.0246875.s001
#
# Spanish young adults, N=185. Three raw-item scales:
#   faces -- FACES (Family Adaptability and Cohesion Evaluation Scale,
#            20 items), already numeric 1-5.
#   eds   -- Differentiation of Self Scale (EDS, the paper's focal
#            instrument, 74 items), already numeric 1-6.
#   stai  -- State-Trait Anxiety Inventory (20 items), already numeric
#            0-3.
# One raw item (`EDCS_34`) is a naming typo for EDS item 34 (same 1-6
# range as every other EDS item), renamed for consistency.
# COHESION_total/ADAPTABILIDAD_total/FACES_total/RE/PY/FO/DO/CE/
# EDS_total/STAI_total/Z*_total/mod_funcfam_difer are aggregates,
# excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0246875.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Edad": "cov_age", "Sexo": "cov_sex", "Estacivi": "cov_marital_status",
              "Nivelestu": "cov_education", "Tipofam": "cov_family_type"}

SCALES = {
    "dolzdelcastellar_2021_faces": [f"FACES_{i}" for i in range(1, 21)],
    "dolzdelcastellar_2021_stai": [f"STAI_{i}" for i in range(1, 21)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", "EDCS_34": "EDS_34", "EDS65": "EDS_65", **COV_RENAME})
    return df


def melt_scale(df, cov_cols, item_cols, out_name):
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
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)
    melt_scale(df, cov_cols, [f"EDS_{i}" for i in range(1, 75)], "dolzdelcastellar_2021_eds")


if __name__ == "__main__":
    convert()
