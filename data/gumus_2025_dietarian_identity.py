#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0327116
# DOI: 10.1371/journal.pone.0327116
# Gumus, Macit, Demirci & Kizil (2025), "Validation and adaptation of a
# Turkish version of the dietarian identity questionnaire", PLOS ONE.
# CC BY 4.0. N=487, 33-item Dietarian Identity Questionnaire (DIQ), already
# numerically recoded (1-7) in the DIQ##value columns (the plain DIQ##
# columns hold the original text-Likert labels for the same items).
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0327116.s002

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "irw-batch/1.0 (research)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0327116.s002"


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"No": "id", "Age": "cov_age", "Gender": "cov_gender",
                             "Employement": "cov_employment", "dietarypattern": "cov_diet_pattern"})

    item_cols = [c for c in df.columns if c.startswith("DIQ") and c.endswith("value")]
    cov_cols = ["cov_age", "cov_gender", "cov_employment", "cov_diet_pattern"]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("value", "", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    path = OUT_DIR / "gumus_2025_dietarian_identity.csv"
    long.to_csv(path, index=False)
    print(f"gumus_2025_dietarian_identity.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
