#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0212304
# DOI: 10.1371/journal.pone.0212304
# Supporting Information: https://doi.org/10.1371/journal.pone.0212304.s001
#
# Automated triage flagged this as low-confidence id mapping; id is
# clean/unique once a single row with a missing respondentnr is dropped
# (567/567 remaining). Raw file has the full 21-item Beck Depression
# Inventory (bdi1r-21r). total_bdi and all derived cognitive/somatic
# symptom-type/z-score columns (nfc_*, dcog_ti, dsom_ti, Z*) are
# aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0212304.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"age_screening": "cov_age", "gender": "cov_gender"}
ITEM_COLS = [f"bdi{i}r" for i in range(1, 22)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"respondentnr": "id", **COV_RENAME})
    return df.dropna(subset=["id"])


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "van_der_donk_2019_bdi.csv", index=False)
    print(f"van_der_donk_2019_bdi.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
