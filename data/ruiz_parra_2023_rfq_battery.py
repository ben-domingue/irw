#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0274378
# DOI: 10.1371/journal.pone.0274378
# Supporting Information: https://doi.org/10.1371/journal.pone.0274378.s009
#
# The raw file's "Spanish RFQ non-clinical" sheet (N=605) bundles nine
# validated instruments administered to overlapping subsamples: RFQ-8
# (everyone, N=605), IPO-83, MAAS, IRI (perspective-taking subscale),
# TAS-20, SCL-90-R, BDI-II, PID-5-BF, and IIP-32 (each answered by a
# smaller subsample, N=254-324 -- confirmed via per-scale missingness,
# which is uniform across every item within a scale, i.e. a genuine
# administration pattern rather than random non-response). Per the IRW
# standard (one scale per file), this produces nine output files. The
# "Retest RFQ non-clinical" and "Spanish RFQ clinical" sheets (smaller
# supplementary samples) are not processed here.
#
# IRI perspective-taking items are recorded as letters A-E (lowest to
# highest); recoded to 1-5. RFQ-8 item 4 has a single stray -9 value
# (isolated to one item, one respondent, otherwise clean 1-7 range) --
# a data-entry error, dropped per datastandard.md's data-entry-error rule.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0274378.s009")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "ruiz_parra_2023_rfq8": "RFQ8",
    "ruiz_parra_2023_ipo83": "IPO83",
    "ruiz_parra_2023_maas": "MAAS",
    "ruiz_parra_2023_tas20": "TAS20",
    "ruiz_parra_2023_scl90r": "SCL90R",
    "ruiz_parra_2023_bdi2": "BDIII",
    "ruiz_parra_2023_pid5bf": "PID5BF",
    "ruiz_parra_2023_iip32": "IIP32",
}

IRI_LETTER_MAP = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Spanish RFQ non-clinical")
    df = df.rename(columns={"Subject": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    return df


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_data()

    # RFQ-8: drop the single -9 data-entry error before melting.
    for c in [c for c in df.columns if c.startswith("RFQ8")]:
        df.loc[df[c] == -9, c] = float("nan")

    # IRI perspective-taking items are letter-coded A-E; recode to 1-5.
    iri_cols = [c for c in df.columns if c.startswith("IRI_PT")]
    for c in iri_cols:
        df[c] = df[c].map(IRI_LETTER_MAP)

    for out_name, prefix in SCALES.items():
        item_cols = [c for c in df.columns if c.startswith(prefix)]
        melt_scale(df, item_cols, f"{out_name}.csv")

    melt_scale(df, iri_cols, "ruiz_parra_2023_iri_pt.csv")


if __name__ == "__main__":
    convert()
