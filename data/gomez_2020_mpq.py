#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0229470
# DOI: 10.1371/journal.pone.0229470
# Supporting Information: https://doi.org/10.1371/journal.pone.0229470.s001
#
# Multidimensional Personality Questionnaire (MPQ) brief-form item pool,
# binary True/False items. The source SPSS value-label metadata is
# corrupted for 18 of 132 M-prefixed columns (nonsense labels like
# "Company"/"Plane"/"Blisters" show up instead of True/False) -- those 18
# are dropped entirely; the remaining 114 have a clean, consistent
# {2.0, 'True'} category set across every one, confirmed by checking the
# exact category set per column (not just eyeballing a few). Mapped
# True=1, 2.0=0 (the residual numeric code with the binary item -- only
# two states, and 1.0 never appears bare, so 2.0 is the file's own
# stand-in for the "False" state despite the label metadata nominally
# saying 0=False/1=True; treated as 0/1 either way since only relative
# ordering within the item matters).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0229470.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_TF = {"True": 1, 2.0: 0}
COV_RENAME = {"AGE": "cov_age", "SEX": "cov_sex"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    # The raw file has each respondent's row duplicated exactly (415 rows,
    # 214 after a full-row drop_duplicates -- confirmed not partial/
    # differing duplicates, a plain export artifact).
    df = df.drop_duplicates().dropna(subset=["ID"])
    return df.rename(columns={"ID": "id", **COV_RENAME})


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    mcols = [c for c in df.columns if c.startswith("M") and c[1:].isdigit()]
    clean_cols = [c for c in mcols
                  if set(df[c].dropna().unique().tolist()) == {2.0, "True"}]
    print(f"{len(clean_cols)} of {len(mcols)} M-items have clean True/False categories")

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=clean_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(MAP_TF)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "gomez_2020_mpq.csv", index=False)
    print(f"gomez_2020_mpq.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
