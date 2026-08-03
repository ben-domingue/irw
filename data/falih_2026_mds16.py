#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/8YLSMK
# DOI: 10.7910/DVN/8YLSMK
# License: CC0 1.0
#
# Maladaptive Daydreaming Scale-16 (MDS-16), 16 items, 0-10 scale.
# Raw file also contains DASS-21 (separate instrument, different response
# scale) -- shipped as its own file, falih_2026_dass21.py, per
# datastandard.md's "one instrument per file" rule.
#
# Six columns in the raw file (MDS16, DASS21, DEPRESSI, ANXIETY, STRESS,
# V52) are all-null section-header artifacts from the source spreadsheet,
# not data -- dropped rather than shipped as empty items/covariates.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

FILE_URL = "https://dataverse.harvard.edu/api/access/datafile/13638063"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MDS_ITEMS = [f"Q{i}" for i in range(1, 17)]
COV_MAP = {
    "NO": "id", "AGE": "cov_age", "AGEGROUP": "cov_agegroup",
    "SEX": "cov_sex", "MARITALS": "cov_marital_status",
    "EXPERIEN": "cov_experien", "V7_A": "cov_v7_a",
    "SMOKING": "cov_smoking", "ALCOHOL": "cov_alcohol",
}
COV_COLS = [v for k, v in COV_MAP.items() if v != "id"]


def convert():
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.BytesIO(r.content), sep="\t")
    df = df.rename(columns=COV_MAP)

    assert df["id"].nunique() == len(df), "id not unique"

    long = df.melt(id_vars=["id"] + COV_COLS, value_vars=MDS_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 10)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + COV_COLS]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "falih_2026_mds16.csv"
    long.to_csv(out_path, index=False)
    print(f"falih_2026_mds16: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
