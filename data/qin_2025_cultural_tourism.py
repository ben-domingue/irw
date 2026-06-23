#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/Questionnaire_Results_/26396855
# DOI (data): 10.1371/journal.pone.0336220.s002
# DOI (paper): 10.1371/journal.pone.0336220
# License: CC BY 4.0
# Authors: Lei Qin, Hongmei Zhang (2025)
# Dataset: Questionnaire on rich cultural tourism experience, cultural identity,
#          tourist satisfaction, behavioral intention, and perceived cultural distance
#          (547 participants, 17 Likert items on a 1-6 scale)
# Five scales: PCD (3 items), CI (3 items), RCTE (5 items), SA (3 items), BI (3 items)

import os
import io
import requests
import pandas as pd

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

# Direct download via DOI redirect (resolves to PLOS GCS signed URL)
DATA_URL = "https://doi.org/10.1371/journal.pone.0336220.s002"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    r = requests.get(DATA_URL, headers=HEADERS)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))

    # id column: 'No.' is participant number
    df = df.rename(columns={"No.": "id"})

    # No covariate columns in this dataset

    # Five scales and their items (all 1-6 Likert scale)
    scales = {
        "qin_2025_perceived_cultural_distance": ["PCD1", "PCD2", "PCD3"],
        "qin_2025_cultural_identity": ["CI1", "CI2", "CI3"],
        "qin_2025_rich_cultural_tourism_experience": ["RCTE1", "RCTE2", "RCTE3", "RCTE4", "RCTE5"],
        "qin_2025_tourist_satisfaction": ["SA1", "SA2", "SA3"],
        "qin_2025_behavioral_intention": ["BI1", "BI2", "BI3"],
    }

    for out_name, item_cols in scales.items():
        long = df[["id"] + item_cols].melt(
            id_vars=["id"],
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        # Filter to valid range (1-6)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 6)].reset_index(drop=True)

        # Enforce column order
        long = long[["id", "item", "resp"]]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(
            f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
            f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
        )


if __name__ == "__main__":
    convert()
