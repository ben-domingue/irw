#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249272
# DOI: 10.1371/journal.pone.0249272
# Supporting Information: https://doi.org/10.1371/journal.pone.0249272.s001
#
# 61-item Mentalized Affectivity Scale (MAS, the paper's focal
# instrument, Italian validation), used as the raw 1-61 sequence
# (including the 15 reverse-worded items, e.g. Mas_9R) with no direction
# recoding -- the IRW standard only requires consistent direction WITHIN
# an item, not across items, so reverse-worded items don't need fixing.
# A separately-recoded "_Rib" twin exists for each reverse item (Italian
# "ribaltato" = flipped) but was NOT used: 3 of the 15 (_40, _44, _56)
# have a single wildly out-of-range value (124, 107, 51 on an otherwise
# clean 1-7 scale) -- a data-entry/recoding artifact per
# datastandard.md's cross-item consistency check -- so using the raw
# columns sidesteps that corruption entirely rather than patching around
# it. Everything else in the file (Mas_identifying/processing/expression,
# ERQ_*, I_TIPI_*, SWLS_Totale, Somma*, RFQ_C/u) is a subscale/total
# aggregate -- no other raw item sets present.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0249272.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Gender": "cov_gender", "Job": "cov_job", "Education": "cov_education"}

REVERSED = {9, 13, 15, 19, 20, 24, 31, 32, 36, 39, 40, 44, 53, 55, 56}
ITEM_COLS = [f"Mas_{i}R" if i in REVERSED else f"Mas_{i}" for i in range(1, 62)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"id_num": "id", **COV_RENAME})


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "rinaldi_2021_mas.csv", index=False)
    print(f"rinaldi_2021_mas.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
