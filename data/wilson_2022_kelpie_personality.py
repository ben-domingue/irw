#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0267266
# DOI: 10.1371/journal.pone.0267266
# Supporting Information: https://doi.org/10.1371/journal.pone.0267266.s002
#
# Owners rate their working Kelpie's personality/ability traits on a 1-5
# scale. The focal unit (`id`) is the dog, not the owner -- the owner is an
# external rater, so OwnerCode maps to `rater` rather than `cov_*`.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0267266.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Age_yrs": "cov_age_years",
    "Sex": "cov_sex",
    "Work_type": "cov_work_type",
}

ITEM_COLS = ["Confidence_stock", "Calmness_stock", "Intelligence_stock",
             "Trainability_stock", "Boldness_stock", "Patience_stock",
             "Timidness_stock", "Persistence_stock", "Hyperactivity_stock",
             "Initiative_stock", "Excitability_stock", "Obedience_stock",
             "Nervousness_stock", "Impulsiveness_stock", "Sociability",
             "Friendliness", "Stamina", "Overall_ability"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"DogCode": "id", "OwnerCode": "rater", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id", "rater"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"] + cov_cols + ["rater"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "wilson_2022_kelpie_personality.csv"
    long.to_csv(out_path, index=False)
    print(f"wilson_2022_kelpie_personality.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
