#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0286160
# DOI: 10.1371/journal.pone.0286160
# Supporting Information: https://doi.org/10.1371/journal.pone.0286160.s001
#
# The raw file also carries Big Five subscale SUM scores (extraversion,
# agreeableness, Conscientiousness, Neuroticism, openness) -- those are
# aggregate composites, not item-level responses, and are dropped per the
# IRW standard's "no aggregate/subscale totals" rule. Only the per-substance
# use checklist is genuine item-level (binary) data.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0286160.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "GEND1": "cov_gender",
    "College": "cov_college",
    "AGE": "cov_age",
    "Educationyrs": "cov_education_years",
    "employment": "cov_employment",
    "Residence": "cov_residence",
    "Income": "cov_income_source",
    "marital": "cov_marital_status",
}

# Substance checklist items. "AnySubstance" is itself a derived "used any
# substance" summary flag, not a specific substance -- excluded as an
# aggregate, same reasoning as the Big Five sums.
ITEM_COLS = ["CIGARETTEANDOTHER", "ALCOHOL", "TRANQUILIZERS", "SEDATIVE",
             "AMPHETAMINE", "CANNABIS", "HALLUCINOGEN", "COCAINE", "HEROINE",
             "OPIUM", "VOLALITEINHALANTS", "INJECTABLE"]

YES_NO_MAP = {"Yes": 1, "No": 0}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"Case": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for c in ITEM_COLS:
        df[c] = df[c].replace(YES_NO_MAP)
        df[c] = pd.to_numeric(df[c], errors="coerce")

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "kinyanjui_2023_substance_use.csv"
    long.to_csv(out_path, index=False)
    print(f"kinyanjui_2023_substance_use.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
