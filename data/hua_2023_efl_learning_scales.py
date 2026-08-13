#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280919
# DOI: 10.1371/journal.pone.0280919
# Supporting Information: https://doi.org/10.1371/journal.pone.0280919.s001 (S1 Dataset, SPSS .sav)
#
# Hua & Wang (2023), "The relationship between Chinese university students'
# learning preparation and learning achievement within the EFL blended
# teaching context in COVID-19 post-epidemic era: The mediating effect of
# learning methods". n=942 survey responses. The raw "index" column is NOT
# a unique respondent id (942 rows, only 481 distinct index values, and rows
# sharing an index value have entirely different response profiles) -- it
# resets/repeats across batches, so the row position is used as `id` instead
# (per datastandard.md "Identify and set the person ID column").
#
# Four validated instruments are present, each split into its own output
# file (one file per scale/instrument):
#   1. EFL Academic Self-Concept (EFL-ASC): 26 items across 5 factors
#      (general, listening, writing, speaking, reading). Paper text says
#      "5-point Likert" but the raw data consistently uses 6 response
#      categories on every single item (cross-item value_counts confirm the
#      6th category is a real, proportionally-recurring response, not a
#      sentinel) -- the data is trusted over the paper's scale description.
#   2. EFL Course Experience Questionnaire (EFL-CEQ): good teaching (6),
#      generic skills (6), clear goals/standards (4) = 16 items, 5-point.
#      The 4th factor, "overall satisfaction", has only 1 item
#      (EFL_CE_Overall_S_Q1) and is dropped per the no-single-item-scale rule.
#   3. EFL Study Engagement Scale (EFL-SESS): vigor (5), dedication (5),
#      absorption (4) = 14 items, 7-point.
#   4. EFL Academic Procrastination Scale (EFL-APS): 3 items, 5-point.
#
# Excluded: subscale total/aggregate columns (EFL_W, EFL_L, EFL_S, EFL_R,
# General_EFL_ASC, EFL_CE_*, EFL_LE_*), "LA" (final exam score, a composite
# outcome not a raw item response), "Gender", "totalseconds" (whole-survey
# completion time, out of rt's scope per pipeline convention).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = "https://doi.org/10.1371/journal.pone.0280919.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "hua_2023_efl_academic_self_concept": [
        "General_EFL_ASC_Q1", "General_EFL_ASC_Q2", "General_EFL_ASC_Q3",
        "General_EFL_ASC_Q4", "General_EFL_ASC_Q5", "General_EFL_ASC_Q6",
        "General_EFL_ASC_Q7",
        "EFL_W_Q1", "EFL_W_Q2", "EFL_W_Q3", "EFL_W_Q4", "EFL_W_Q5", "EFL_W_Q6",
        "EFL_L_Q1", "EFL_L_Q2", "EFL_L_Q3", "EFL_L_Q4", "EFL_L_Q5", "EFL_L_Q6",
        "EFL_S_Q1", "EFL_S_Q2", "EFL_S_Q3",
        "EFL_R_Q1", "EFL_R_Q2", "EFL_R_Q3", "EFL_R_Q4",
    ],
    "hua_2023_efl_course_experience": [
        "EFL_CE_GT_Q1", "EFL_CE_GT_Q2", "EFL_CE_GT_Q3", "EFL_CE_GT_Q4",
        "EFL_CE_GT_Q5", "EFL_CE_GT_Q6",
        "EFL_CE_GS_Q1", "EFL_CE_GS_Q2", "EFL_CE_GS_Q3", "EFL_CE_GS_Q4",
        "EFL_CE_GS_Q5", "EFL_CE_GS_Q6",
        "EFL_CE_CGS_Q1", "EFL_CE_CGS_Q2", "EFL_CE_CGS_Q3", "EFL_CE_CGS_Q4",
    ],
    "hua_2023_efl_study_engagement": [
        "EFL_LE_Vigor_Q1", "EFL_LE_Vigor_Q2", "EFL_LE_Vigor_Q3",
        "EFL_LE_Vigor_Q4", "EFL_LE_Vigor_Q5",
        "EFL_LE_Dedication_Q1", "EFL_LE_Dedication_Q2", "EFL_LE_Dedication_Q3",
        "EFL_LE_Dedication_Q4", "EFL_LE_Dedication_Q5",
        "EFL_LE_Absorption_Q1", "EFL_LE_Absorption_Q2",
        "EFL_LE_Absorption_Q3", "EFL_LE_Absorption_Q4",
    ],
    "hua_2023_efl_academic_procrastination": [
        "EFL_AP_Q1", "EFL_AP_Q2", "EFL_AP_Q3",
    ],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df, _meta = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch_data()
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        item_cols = [c for c in item_cols if c in df.columns]
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]

        path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
