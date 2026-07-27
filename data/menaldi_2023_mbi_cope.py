#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280313
# DOI: 10.1371/journal.pone.0280313
# Supporting Information: https://doi.org/10.1371/journal.pone.0280313.s001
#
# The raw sheet interleaves, for each item, a text-labeled column (the
# item's raw Indonesian response text) with a numerically-coded column
# named after the item's short code (e.g. EE_MBI_1, SD_1) -- confirmed by
# inspection that the coded columns already hold clean numeric scores,
# so only those are used; the text-titled columns are a redundant raw-
# text duplicate of the same responses and are skipped. Selected via
# regex on column name, not position, so column order doesn't matter.
# 22-item Maslach Burnout Inventory (EE/DP/PA subscales) and 28-item
# Brief COPE. Trailing bare-named columns (EE, DP, PA, SD, AC, ...,
# without an item-number suffix) are subscale/total aggregates,
# excluded -- the regex requires a numeric suffix so these don't match.
# No reliable person-ID column ("Inisial nama" is just initials); row
# index used.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0280313.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MBI_PAT = re.compile(r"^(EE|DP|PA)_MBI_\d+$")
COPE_PAT = re.compile(r"^(SD|AC|D|SU|UES|BD|PR|H|V|UIS|R|A|P|SB)_\d+$")


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    mbi_cols = [c for c in df.columns if isinstance(c, str) and MBI_PAT.match(c)]
    cope_cols = [c for c in df.columns if isinstance(c, str) and COPE_PAT.match(c)]

    melt_scale(df, mbi_cols, "menaldi_2023_mbi")
    melt_scale(df, cope_cols, "menaldi_2023_brief_cope")


if __name__ == "__main__":
    convert()
