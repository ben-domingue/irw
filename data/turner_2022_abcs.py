#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0269928
# DOI: 10.1371/journal.pone.0269928
# Supporting Information: https://doi.org/10.1371/journal.pone.0269928.s006
#
# The raw file bundles two item sets: stimulus-response belief-change items
# (Q*_SRchange, 9 items) and cognitive-mediation belief items (Q*_CMgen,
# 15 items). Per the IRW standard (one scale per file), this produces two
# output files.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0269928.s006")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"age": "cov_age", "Sex": "cov_sex", "Ethn": "cov_ethnicity",
              "Job": "cov_job", "Edu": "cov_education", "Marital": "cov_marital"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"Pnumber": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    return df


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_data()
    sr_cols = [c for c in df.columns if c.lower().endswith("srchange")]
    cm_cols = [c for c in df.columns if c.lower().endswith("cmgen")]
    melt_scale(df, sr_cols, "turner_2022_sr_belief_change.csv")
    melt_scale(df, cm_cols, "turner_2022_cognitive_mediation.csv")


if __name__ == "__main__":
    convert()
