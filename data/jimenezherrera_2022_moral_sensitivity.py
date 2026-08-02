#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0270049
# DOI: 10.1371/journal.pone.0270049
# Jimenez-Herrera, Font-Jimenez, Bazo-Hernandez, Roldan-Merino, Biurrun-Garrido
# & Hurtado-Pardos (2022), "Moral sensitivity of nursing students. Adaptation
# and validation of the moral sensitivity questionnaire in Spain", PLOS ONE.
# CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0270049.s001

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "irw-batch/1.0 (research)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0270049.s001"

COV_MAP = {
    "Code": "id",
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Academic year": "cov_academic_year",
    "Center": "cov_center",
    "Study schedule": "cov_study_schedule",
    "Currently employed": "cov_currently_employed",
    "Previous work experience in healthcare": "cov_prior_healthcare_experience",
    "Type of contract": "cov_contract_type",
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns=COV_MAP)

    item_cols = [c for c in df.columns if c.startswith("Item Moral")]
    cov_cols = list(COV_MAP.values())[1:]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    path = OUT_DIR / "jimenezherrera_2022_moral_sensitivity.csv"
    long.to_csv(path, index=False)
    print(f"jimenezherrera_2022_moral_sensitivity.csv: rows={len(long)} "
          f"ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
