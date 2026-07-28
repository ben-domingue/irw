#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0276803
# DOI: 10.1371/journal.pone.0276803
# Supporting Information: https://doi.org/10.1371/journal.pone.0276803.s001
#
# The raw file bundles three scales administered to Japanese nurses caring
# for COVID-19 patients: the Fear of COVID-19 Scale (FCV19S, 7 items,
# 1-5), the Hospital Anxiety and Depression Scale (HADS, 14 items, 0-4),
# and a 60-item Japanese Big Five Scale (BFS, 1-7). Per the IRW standard
# (one scale per file), this produces three output files.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0276803.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"age": "cov_age", "sex": "cov_sex"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
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

    fcv_cols = [c for c in df.columns if c.startswith("FCV19S")]
    hads_cols = [c for c in df.columns if c.startswith("HADS")]
    bfs_cols = [c for c in df.columns if c.startswith("BFS")]

    melt_scale(df, fcv_cols, "odachi_2022_fear_covid19.csv")
    melt_scale(df, hads_cols, "odachi_2022_hads.csv")
    melt_scale(df, bfs_cols, "odachi_2022_bfs.csv")


if __name__ == "__main__":
    convert()
