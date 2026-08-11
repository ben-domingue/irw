#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0287795
# DOI: 10.1371/journal.pone.0287795
# Supporting Information: https://doi.org/10.1371/journal.pone.0287795.s007
#
# Survey of US academic science/engineering faculty asking whether they
# personally hold each of 8 concealable stigmatized identities (CSIs):
# LGBQ+, depression, anxiety, low socioeconomic status, first-generation
# college student, academic struggle, disability, community-college
# transfer. Each is a binary (0/1) self-report item. The "_2" suffixed
# columns are the cleaned binary versions used here (the raw text columns,
# e.g. "depression", contain the same information as free text plus a
# "Decline to state" option, already excluded via NaN in the binary cols).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0287795.s007")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["lgbq", "depression2", "anxiety2", "lowses", "fgen",
             "struggle2", "disability2", "transfer2"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "busch_2023_stigma.csv", index=False)
    print(f"busch_2023_stigma.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
