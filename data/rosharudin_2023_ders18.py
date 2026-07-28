#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0289551
# DOI: 10.1371/journal.pone.0289551
# Supporting Information: https://doi.org/10.1371/journal.pone.0289551.s001
#
# The raw file bundles two scales under obfuscated "@N_LETTER" column
# names: a 21-item DASS-21 (letters S/A/D = Stress/Anxiety/Depression
# subscale, 0-4) and the 18-item DERS-18 (letters A/C/G/I/NA/S = the six
# DERS subscales Awareness/Clarity/Goals/Impulse/Nonacceptance/Strategies,
# 1-5) -- confirmed by matching subscale-letter counts and ranges against
# the two named instruments in the paper title. Per the IRW standard (one
# scale per file), this produces two output files.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0289551.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DASS21_COLS = ["@1_S", "@2_A", "@3_D", "@4_A", "@5_D", "@6_S", "@7_A", "@8_S",
               "@9_A", "@10_D", "@11_S", "@12_S", "@13_D", "@14_S", "@15_A",
               "@16_D", "@17_D", "@18_S", "@19_A", "@20_A", "@21_D"]
DERS18_COLS = ["@1_A", "@2_C", "@3_C", "@4_A_A", "@5_C", "@6_A", "@7_NA",
               "@8_G", "@9_I", "@10_S", "@11_S_A", "@12_G", "@13_NA",
               "@14_NA", "@15_G", "@16_I", "@17_S", "@18_I"]

COV_RENAME = {"Jantina": "cov_gender", "Tingkatan": "cov_form",
              "Kaum": "cov_ethnicity", "Agama": "cov_religion"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"id": "id", **COV_RENAME})
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
    melt_scale(df, DASS21_COLS, "rosharudin_2023_dass21.csv")
    melt_scale(df, DERS18_COLS, "rosharudin_2023_ders18.csv")


if __name__ == "__main__":
    convert()
