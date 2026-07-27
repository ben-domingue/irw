#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0149913
# DOI: 10.1371/journal.pone.0149913
# Supporting Information: https://doi.org/10.1371/journal.pone.0149913.s001
#
# Automated triage flagged this as low-confidence id mapping; `id` is
# actually clean and unique (5897/5897). Raw file has the 40-item Hamburg
# Burnout Inventory (HBI, German instrument with 10 subscales) and the
# 10-item Major Depression Inventory (MDI). Items f19/f24 have a separate
# reverse-coded twin (f19_umgepo/f24_umgepo) at their position in the 1-40
# item sequence -- the recoded versions are used (matching their sequence
# position), the raw un-recoded f19/f24 columns kept elsewhere in the file
# are redundant with these and skipped. mdi_4_5 (a combined-for-scoring
# variant of items 4 and 5) is likewise skipped in favor of the individual
# mdi4_neu/mdi5_neu items. All *_sum/_nom/_Ph/percentile/severity columns
# (EE, PA_neu, DIST, ..., MD_DSM, HBI_sum, BO_Phase, ...) are derived
# subscale/diagnostic aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0149913.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"sex_code": "cov_sex", "age": "cov_age", "employment": "cov_employment"}

HBI_COLS = ([f"f{i}" for i in range(1, 19)] + ["f19_umgepo"] +
            [f"f{i}" for i in range(20, 24)] + ["f24_umgepo"] +
            [f"f{i}" for i in range(25, 41)])
MDI_COLS = [f"mdi{i}_neu" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


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
    df = df.rename(columns=COV_RENAME)
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype(int)
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, HBI_COLS, "wurm_2016_hbi")
    melt_scale(df, cov_cols, MDI_COLS, "wurm_2016_mdi")


if __name__ == "__main__":
    convert()
