#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0233359
# DOI: 10.1371/journal.pone.0233359
# Supporting Information: https://doi.org/10.1371/journal.pone.0233359.s001
#
# Automated triage flagged this as low-confidence id mapping; id is
# clean/unique (371/371). Raw file has secf_1m..secf_10m (10 items, 0-3
# scale, financial-security-related). f1-f4 are continuous IRT/factor
# scores (not raw items -- hundreds of distinct non-integer values), and
# fdsecureraw/dpsscore are aggregate sums -- excluded. A separate small
# item set (SECA_7, SECA_9, SECA_11, SECJ_1) appears to be a scattered
# leftover from the CFPB Financial Well-Being item bank but is far too
# incomplete (4 non-consecutive items out of that bank's much larger set)
# to be usable as a coherent instrument -- not included.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0233359.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"GENDER": "cov_gender", "age": "cov_age", "race": "cov_race"}
ITEM_COLS = [f"secf_{i}m" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_sas(io.BytesIO(r.content), format="sas7bdat")


def convert():
    df = fetch_data()
    df = df.rename(columns={"SUBJECT": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "weida_2020_financial_security.csv", index=False)
    print(f"weida_2020_financial_security.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
