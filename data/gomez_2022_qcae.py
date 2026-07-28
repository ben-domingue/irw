#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0261914
# DOI: 10.1371/journal.pone.0261914
# Supporting Information: https://doi.org/10.1371/journal.pone.0261914.s002
#
# The raw file has the 31 raw Questionnaire of Cognitive and Affective
# Empathy (QCAE) items (some already reverse-scored at source, marked with
# an "r" suffix -- kept as-is, not re-reversed, per datastandard.md). Every
# other instrument in the file (TOSCA, SIAS-6, SPS-6, BIS/BAS, ERQ, ATQ) is
# present only as subscale totals/means, not raw items, and is excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0261914.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

QCAE_COLS = ["QCAE15", "QCAE16", "QCAE19", "QCAE20", "QCAE21", "QCAE22",
             "QCAE24", "QCAE25", "QCAE26", "QCAE27", "QCAE1r", "QCAE3",
             "QCAE4", "QCAE5", "QCAE6", "QCAE18", "QCAE28", "QCAE30",
             "QCAE31", "QCAE8", "QCAE9", "QCAE13", "QCAE14", "QCAE2r",
             "QCAE11", "QCAE17r", "QCAE29r", "QCAE7", "QCAE10", "QCAE12",
             "QCAE23"]

COV_RENAME = {"Gender": "cov_gender", "Age": "cov_age", "RelStatus": "cov_rel_status",
              "EduLevel": "cov_education", "EmpStatus": "cov_employment"}

LIKERT_MAP = {"Strongly Disagree": 1, "Slightly Disagree": 2,
              "Slightly Agree": 3, "Strongly Agree": 4}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    for c in QCAE_COLS:
        if df[c].dtype.name == "category" or df[c].dtype == object:
            df[c] = df[c].astype(str).map(LIKERT_MAP)

    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=QCAE_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "gomez_2022_qcae.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
