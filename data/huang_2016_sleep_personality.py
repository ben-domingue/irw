#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0157238
# DOI: 10.1371/journal.pone.0157238
# Supporting Information: https://doi.org/10.1371/journal.pone.0157238.s001
#
# The raw file bundles three raw-item scales (NEO-FFI Neuroticism, NEO-FFI
# Conscientiousness, CES-D) plus the Pittsburgh Sleep Quality Index, whose
# item-level components are stored as free-text frequency labels mixed with
# already-computed component/total scores -- not processed here (PSQ_5a-j
# etc. would need a text->numeric mapping and separation from the PSQI
# component scores, which are aggregates). Per the IRW standard (one scale
# per file), this produces three output files: NEO Neuroticism, NEO
# Conscientiousness, CES-D.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0157238.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Age": "cov_age", "Sex": "cov_sex", "Race": "cov_race",
              "Language": "cov_language", "Years_Edu": "cov_years_edu"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"Code": "id", **COV_RENAME})
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
    n_cols = [f"N{i}" for i in range(1, 13)]
    c_cols = [f"C{i}" for i in range(1, 13)]
    cesd_cols = [f"CESD_{i}" for i in range(1, 21)]

    melt_scale(df, n_cols, "huang_2016_neo_neuroticism.csv")
    melt_scale(df, c_cols, "huang_2016_neo_conscientious.csv")
    melt_scale(df, cesd_cols, "huang_2016_cesd.csv")


if __name__ == "__main__":
    convert()
