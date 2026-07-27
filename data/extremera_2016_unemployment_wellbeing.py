#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0163656
# DOI: 10.1371/journal.pone.0163656
# Supporting Information: https://doi.org/10.1371/journal.pone.0163656.s001
#
# Four raw-item scales among unemployed adults, N≈1123: Subjective
# Happiness Scale (SHS, 4 items), Satisfaction With Life Scale (SWLS, 5
# items), Emotional Intelligence scale (16 items, "ie16" in the raw file
# is the 16th EI item -- a naming typo, not a different construct;
# renamed to ei16), Suicide Behaviours Questionnaire (SBQ, 4 items).
#
# `cuestionario` (retriage's "id") is NOT a person identifier -- rows
# sharing the same cuestionario value have different ages/sexes (spot-
# checked directly), so it's some kind of batch/version code, and using
# it as id would incorrectly merge up to 10 different unemployed adults
# into one. No real repeated-measures/wave structure exists either (no
# person is genuinely re-surveyed). Row index used as id instead; this
# is a single cross-sectional sample, not longitudinal. IE_total,
# Happiness_Scores, LifeSatisfaction_Scores, SuicideBehaviours_Scores,
# and the Z*/Sat_IE/Fel_IE columns are all derived aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0163656.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"age": "cov_age", "sex": "cov_sex", "marital_status": "cov_marital_status",
              "length_unemployment": "cov_length_unemployment",
              "unemployment_benefits": "cov_unemployment_benefits",
              "level_education": "cov_education"}

SCALES = {
    "extremera_2016_shs": [f"shs{i}" for i in range(1, 5)],
    "extremera_2016_swls": [f"swls{i}" for i in range(1, 6)],
    "extremera_2016_sbq": [f"sbq{i}" for i in range(1, 5)],
}
EI_COLS = [f"ei{i}" for i in range(1, 16)] + ["ie16"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"ie16": "ei16", **COV_RENAME})
    df["id"] = df.index
    return df


def melt_scale(df, cov_cols, item_cols, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)
    melt_scale(df, cov_cols, [f"ei{i}" for i in range(1, 17)], "extremera_2016_ei")

    # SWLS is a standard 1-7 scale; resp==0 occurs twice total (swls3,
    # swls5), isolated against ~5600 legitimate 1-7 responses -- a
    # data-entry error, dropped post-hoc rather than re-melting.
    swls_path = OUT_DIR / "extremera_2016_swls.csv"
    swls = pd.read_csv(swls_path)
    swls = swls[swls["resp"] != 0].reset_index(drop=True)
    swls.to_csv(swls_path, index=False)
    print(f"extremera_2016_swls.csv (post-fix): ids={swls['id'].nunique()} "
          f"items={swls['item'].nunique()} resp={swls['resp'].min()}-{swls['resp'].max()}")


if __name__ == "__main__":
    convert()
