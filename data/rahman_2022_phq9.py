#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0269634
# DOI: 10.1371/journal.pone.0269634
# Supporting Information: https://doi.org/10.1371/journal.pone.0269634.s006
#
# No reliable person-ID column: `Timestamp` is present for only 333 of 677
# rows (missing entirely for what looks like a second collection batch),
# so it can't serve as id either -- row index used instead. PHQ-9 (9
# items, text-coded) is complete across all 677 rows. `gad` is an
# aggregate total (range 0-21, matches a full GAD-7 sum) with no
# corresponding raw GAD items present in the file, excluded; `gfi` is a
# broken/constant column (same value on every row), ignored.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0269634.s006")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_PHQ = {"Not at all": 0, "Several Days (1-5 days)": 1,
           "more than half days (6-10 days)": 2, "Nearly everyday (11-14 days)": 3}

COV_RENAME = {"Age": "cov_age", "Gender": "cov_gender", "Education": "cov_education"}
ITEM_COLS = [f"PHQ_{i}" for i in range(1, 10)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_stata(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def convert():
    df = fetch_data()
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(MAP_PHQ)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "rahman_2022_phq9.csv", index=False)
    print(f"rahman_2022_phq9.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
