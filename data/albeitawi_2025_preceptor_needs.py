from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0337101
# DOI: 10.1371/journal.pone.0337101
# Albeitawi et al. (2025), "Assessment of clinical medical education needs
# inform design of a preceptor development program in Jordan". S1 Table
# "Original Data for all universities". CC BY 4.0. N=400 clinical educators
# across 6 Jordanian universities/hospitals. Needs-assessment questionnaire:
# 7 teaching-domain items each rated on a 4-point ordinal priority scale
# (Not a priority / Low / Medium / High priority), recoded 1-4.
OUT_NAME = "albeitawi_2025_preceptor_needs"
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0337101.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [
    "Lecturing for large groups ",
    "Tutorial for small groups",
    "Bedside teaching (learning in the clinical setting)",
    "Providing feedback",
    "Assessment in clinical setting ",
    "Clinical simulation ",
    "Mentoring skills ",
]

PRIORITY_MAP = {
    "Not a priority": 1,
    "Low priority": 2,
    "Medium priority": 3,
    "High priority": 4,
}

COV_RENAME = {
    "University": "cov_university",
    "Kindly indicate your gender\n": "cov_gender",
    "Kindly indicate your specialty according to core board certification\n": "cov_specialty_category",
    "Kindly indicate your years of expertise as a clinical educator \n": "cov_years_experience",
    "Kindly indicate the health sector you currently work at\n": "cov_health_sector",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    # No usable person ID column ("Column1" resets/repeats across
    # universities and is not unique across the full sheet) -- use row index.
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in COV_RENAME.values() if c in df.columns]

    # Recode text priority levels to an ordinal 1-4 scale.
    for c in ITEM_COLS:
        df[c] = df[c].astype(str).str.strip().map(PRIORITY_MAP)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.strip()
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{OUT_NAME}.csv"
    long.to_csv(out_path, index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
