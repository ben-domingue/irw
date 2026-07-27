#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0252809
# DOI: 10.1371/journal.pone.0252809
# Supporting Information: https://doi.org/10.1371/journal.pone.0252809.s002
#
# Automated triage flagged this as low-confidence id mapping; id is
# clean/unique (798/798). Raw file has the 10-item Perceived Stress Scale
# (Perc1-10, text-coded). Anxiety/Psycho/Stress columns are aggregate
# totals (ranges 0-19/0-27/0-29), not items. The rest of the file is
# heterogeneous single-question survey items (COVID-related worry,
# equipment adequacy, media type, etc.), not a coherent multi-item scale.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0252809.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_PSS = {"Never": 0, "Almost Never": 1, "Sometimes": 2, "Fairly Often": 3, "Very Often": 4}

COV_RENAME = {"sex": "cov_sex", "age": "cov_age", "profession": "cov_profession",
              "exprience": "cov_experience"}

ITEM_COLS = [f"Perc{i}" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns=COV_RENAME)
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(MAP_PSS)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "teshome_2021_pss10.csv", index=False)
    print(f"teshome_2021_pss10.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
