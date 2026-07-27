#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0223043
# DOI: 10.1371/journal.pone.0223043
# Supporting Information: https://doi.org/10.1371/journal.pone.0223043.s001
#
# SF-36 raw items (36 items, N=200), sickle cell disease patients. Each
# item has its own internally-consistent response range per the standard
# SF-36 format (some binary, some 3/5/6-point) -- not a shared range
# across items, which is expected for this instrument. `sf1` has one
# stray "END" text value (a survey-export artifact, not a real response)
# filtered out. sf24r/sf27r/sf28r/sf32r (recoded duplicates) and all
# subscale/summary columns (SFPhys, SFRole, ..., Health State, gamble/
# ordinal valuations) are derived, excluded.
#
# No id column in this file at all; row index used. The companion S2
# file (covariates + PHQ9/GAD7/SGH totals) has the same row count (200)
# but no confirmed shared key or matching order with S1 -- not merged in,
# to avoid silently misaligning two different patients' records.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0223043.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"sf{i}" for i in range(1, 37)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df["id"] = df.index
    return df


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "ojelabi_2019_sf36.csv", index=False)
    print(f"ojelabi_2019_sf36.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
