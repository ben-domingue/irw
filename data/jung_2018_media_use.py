#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0200333
# DOI: 10.1371/journal.pone.0200333
# Supporting Information (S1 File, "Raw data"):
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0200333.s001
#
# Jung (2018), "The effect of maternal decisional authority on children's
# vaccination in East Asia". N=2134.
#
# The raw file's "Maternal Decisional Authority (1)/(2)", "Health Literacy
# Factor", "HISB Factor", and "Self-efficacy Factor" columns are
# standardized (mean ~0, sd ~1) Confirmatory-Factor-Analysis factor scores
# -- explicitly confirmed in the Methods text ("CFA... single factor
# decisional authority accounted for 48.7% of the total variance...") --
# i.e. composites, not raw item responses, so they are NOT shipped
# (datastandard.md "Subscale aggregate columns" / composite rule).
#
# The only genuine raw per-item data in this file is the 5-item
# Health-Related Media Use battery (TV/Radio/Newspaper/Books/Internet
# usage in the past week; 1=not at all, 2=1-2 times, 3=more than 3 times).
# All other instruments (Decisional Authority, Self-Efficacy, Health
# Literacy) are present ONLY as their derived factor scores in this file --
# no per-item raw columns for those exist here.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0200333.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Nationality": "cov_nationality",
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Marriage": "cov_marriage",
    "Education": "cov_education",
    "Monthly Income": "cov_income",
}

ITEM_RENAME = {
    "Media Use (TV)": "media_tv",
    "Media Use (Radio)": "media_radio",
    "Media Use (Newspaper)": "media_newspaper",
    "Media Use (Books)": "media_books",
    "Media Use (Internet)": "media_internet",
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    df = df.rename(columns={"CASE ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id not unique"

    cov_present = {k: v for k, v in COV_RENAME.items() if k in df.columns}
    df = df.rename(columns=cov_present)
    cov_cols = list(cov_present.values())

    df = df.rename(columns=ITEM_RENAME)
    item_cols = list(ITEM_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 3)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "jung_2018_media_use.csv"
    long.to_csv(out_path, index=False)

    print(f"jung_2018_media_use: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
