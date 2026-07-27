#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0289123
# DOI: 10.1371/journal.pone.0289123
# Supporting Information: https://doi.org/10.1371/journal.pone.0289123.s002
#
# Raw file has GAD-7, PHQ-9, and an 11-item binary GI-symptom-presence
# checklist (Heartburn, Regurgitation, ... -- the symptoms used to screen
# for functional GI disorders, the paper's focal topic). totalGAD7/
# totalPHQ9 and all the derived overlap/diagnosis classification columns
# (GERD, PDS, EPS, FD, IBS, FGID, Overlap*, GAD, MDD, GAD_MDD) are
# aggregates/diagnoses, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0289123.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Age": "cov_age", "Gender": "cov_gender", "BMI": "cov_bmi"}

GAD_COLS = [f"GAD{i}" for i in range(1, 8)]
PHQ_COLS = [f"PHQ{i}" for i in range(1, 10)]
GI_COLS = ["Heartburn", "Regurgitation", "Epigastricpain", "Epigastricburn",
           "Early_satiation", "Postprandial_Fullness", "Nausea_vomit",
           "Abdopain_bowelchange", "Pain_boweltimes", "Pain_stoolchange",
           "Painrelate_bowel"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"STT": "id", **COV_RENAME}).dropna(subset=["id"])
    # One id (A042) appears twice with genuinely different responses --
    # a duplicate-code data-entry error (no wave/date column exists to
    # suggest real repeated measures), not an exact duplicate row to drop.
    # Disambiguate rather than lose either respondent's data.
    dup_n = df.groupby("id").cumcount()
    df["id"] = df["id"] + dup_n.map({0: "", 1: "-b", 2: "-c"}).fillna("")
    return df


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
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, GAD_COLS, "tran_2023_gad7")
    melt_scale(df, cov_cols, PHQ_COLS, "tran_2023_phq9")
    melt_scale(df, cov_cols, GI_COLS, "tran_2023_gi_symptoms")


if __name__ == "__main__":
    convert()
