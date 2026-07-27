#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0177758
# DOI: 10.1371/journal.pone.0177758
# Supporting Information: https://doi.org/10.1371/journal.pone.0177758.s003
#
# Raw file pools 4 sub-studies of one experiment (physician nonverbal
# empathy manipulation) and bundles 4 distinct scales: Competence (5 items),
# Warmth (4 items), CARE Measure (10 items), and PANAS (20 items, positive +
# negative subscales administered together -- kept as one file per prior
# IRW convention, see data/wu2021_empathy.py). One output file per scale.
#
# The experiment crosses two independent binary manipulations (white coat
# worn: condcoat; empathic nonverbal behavior: condemp) -- IRW's `treat`
# column only supports a single binary factor, so with two crossed factors
# both are kept as covariates rather than collapsing into `treat` and
# losing information about which factor was manipulated.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0177758.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "study": "cov_study",
    "sex": "cov_sex",
    "condcoat": "cov_condition_coat",
    "condemp": "cov_condition_empathy",
}

SCALES = {
    "kraft_todd_2017_competence": [f"COMP{i}" for i in range(1, 6)],
    "kraft_todd_2017_warmth": [f"WARM{i}" for i in range(1, 5)],
    "kraft_todd_2017_care_measure": [f"CARE{i}" for i in range(1, 11)],
}
PANAS_POS = [f"PANASPOS{i}" for i in range(1, 11)]
PANAS_NEG = [f"PANASNEG{i}" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str],
               out_name: str, itemcov: dict | None = None):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    extra = []
    if itemcov:
        for col_name, mapping in itemcov.items():
            long[col_name] = long["item"].map(mapping)
            extra.append(col_name)

    long = long[["id", "item", "resp"] + cov_cols + extra]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"subid": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)

    panas_valence = {**{c: "positive" for c in PANAS_POS},
                     **{c: "negative" for c in PANAS_NEG}}
    melt_scale(df, cov_cols, PANAS_POS + PANAS_NEG, "kraft_todd_2017_panas",
               itemcov={"itemcov_valence": panas_valence})


if __name__ == "__main__":
    convert()
