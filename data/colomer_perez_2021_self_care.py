from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260827
# DOI: 10.1371/journal.pone.0260827
# Colomer-Perez, Useche et al. (2021), "Self-care appraisal in nursing
# assistant students: Adaptation, validation, and evaluation of the
# influencing sociodemographic factors". S1 Dataset. CC BY 4.0. N~920.
#
# Two instruments -> two output files:
#   colomer_perez_2021_asa: Appraisal of Self-Care Agency scale (ASA-A),
#     24 items, 1-5.
#   colomer_perez_2021_soc13: Sense of Coherence-13 (SOC-13; INVSOC-
#     prefixed columns are the same scale's reverse-worded items), 13
#     items, 1-7.
# SOCTOTAL/ASATOTAL (composite totals) and F1-F4 factor scores in the same
# file are derived, not shipped.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0260827.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"SEX": "cov_sex", "AGE": "cov_age"}

SOC_COLS = ["INVSOC1", "INVSOC2", "INVSOC3", "SOC4", "SOC5", "SOC6",
            "INVSOC7", "SOC8", "SOC9", "SOC10", "SOC11", "SOC12", "SOC13"]


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def ship(df, cov_cols, item_cols, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch().rename(columns={"REFER": "id", **COV_MAP})
    df = df.dropna(subset=["id"]).drop_duplicates(subset="id")
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    asa_cols = [f"ASA{i}" for i in range(1, 25) if f"ASA{i}" in df.columns]
    ship(df, cov_cols, asa_cols, "colomer_perez_2021_asa")
    ship(df, cov_cols, SOC_COLS, "colomer_perez_2021_soc13")


if __name__ == "__main__":
    convert()
