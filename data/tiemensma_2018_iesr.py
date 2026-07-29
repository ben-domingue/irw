#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0195229
# DOI: 10.1371/journal.pone.0195229
# Supporting Information: https://doi.org/10.1371/journal.pone.0195229.s001
#
# 22-item Impact of Event Scale-Revised (IES-R), 0-4 scale. The source
# "id" column collides for 2 of 552 rows (different response patterns
# under the same id string, not a re-test/duplicate) so it fails the
# uniqueness check; row index is used as id instead per datastandard.md.
# IES_total/IES_INT/IES_AVD/IES_HYP are derived subscale scores and
# ValidIES is a completion flag -- both dropped, not raw items.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0195229.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"IES{i}" for i in range(1, 23)]
COV_RENAME = {"latino_nonLat": "cov_latino"}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content), convert_categoricals=False)
    df = df.rename(columns=COV_RENAME)

    df = df.drop(columns=["id"]).reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 4)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "tiemensma_2018_iesr.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
