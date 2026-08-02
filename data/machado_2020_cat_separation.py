#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0230999
# DOI: 10.1371/journal.pone.0230999
# Machado, Oliveira, Machado, Ceballos & Sant'Anna (2020), "Identification of
# separation-related problems in domestic cats: A questionnaire survey",
# PLOS ONE. CC BY 4.0. N=223 cats (non-human respondents; id = cat, not owner).
# Only the 7-item separation-related problem-behavior checklist is shipped
# here -- the remaining columns are owner/cat/housing covariates, not part
# of the same construct.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0230999.s002

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "irw-batch/1.0 (research)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0230999.s002"

ITEM_COLS = [
    "Depressive_apathetic", "Agressive", "Excessive_vocalization",
    "Destructive_behavior", "Elimination_problems(urine)",
    "Elimination_problems(feces)", "Agitated_anxious",
]
COV_COLS = ["cov_cat_sex", "cov_cat_age", "cov_breed", "cov_time_with_owner"]


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={
        "Cat_ID": "id", "Cat_sex": "cov_cat_sex", "Cat_age": "cov_cat_age",
        "Breed": "cov_breed", "Time_with_owner": "cov_time_with_owner",
    })

    long = df.melt(id_vars=["id"] + COV_COLS, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + COV_COLS]

    path = OUT_DIR / "machado_2020_cat_separation.csv"
    long.to_csv(path, index=False)
    print(f"machado_2020_cat_separation.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
