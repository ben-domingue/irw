#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0314607
# DOI: 10.1371/journal.pone.0314607
# Supporting Information: https://doi.org/10.1371/journal.pone.0314607.s001
#
# Raw file bundles: an 8-item semantic-differential scale of feelings about
# mask-wearing (Emotion_*), a 3-item physical-contact-behavior set
# (Touching/Contact_with_professionals/Contact_with_unknown), several
# single-item attitude questions on unrelated topics (not a coherent
# multi-item scale each -- excluded), PID-5-BF personality-domain SUM
# scores (Negative_Affectivity, Detachment, Antagonism, Disinhibition,
# Psychoticism) and an MACRF composite (all aggregates, not items --
# excluded per the IRW standard). Only the two genuine multi-item scales
# are converted. A second Supporting Information file (S3, "Network
# analysis") duplicates this same data with opaque column codes (A1, A2,
# B, ...); this script uses S1, which has meaningful item names.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0314607.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Education": "cov_education",
    "Age": "cov_age_group",
    "PastCOVIDinfection": "cov_past_covid_infection",
}

SCALES = {
    "di_riso_2025_mask_emotion": [
        "Emotion_Controlled", "Emotion_Weak", "Emotion_Scared", "Emotion_Silly",
        "Emotion_Brave", "Emotion_Caring", "Emotion_Strong", "Emotion_Protected",
    ],
    "di_riso_2025_contact_behavior": [
        "Touching", "Contact_with_professionals", "Contact_with_unknown",
    ],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
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
    df = df.rename(columns=COV_RENAME)
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)


if __name__ == "__main__":
    convert()
