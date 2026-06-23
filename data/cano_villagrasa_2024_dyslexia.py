#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/27647529
# DOI: 10.6084/m9.figshare.27647529.v2
# License: CC BY 4.0
# Author: Alejandro Cano Villagrasa (2024)
# Dataset: Linguistic and Cognitive abilities in Children with Dyslexia (60 participants:
#          30 with dyslexia + 30 controls). Data are organized as matched pairs: each row
#          contains scores for one dyslexia child (G-DYSLEXIA) and one matched control
#          child (G-CONTROL). Three sheets: Language Skills (5 subtests),
#          Cognitive Competence (5 subtests), Executive Functions (4 subtests).
#
# Each sheet has "Participant ID" 1-60 representing matched pairs.
# We unpack to long format with 120 unique person IDs:
#   dyslexia child = pair_id * 2 - 1
#   control child  = pair_id * 2
# treat column: 1 = dyslexia, 0 = control
#
# Three separate files (one per assessment domain), each treated as a distinct
# cognitive ability scale.

import os
import io
import requests
import pandas as pd

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

# Figshare file ID 50360895 for DATA BASE_Manuscript.xlsx
DATA_URL = "https://ndownloader.figshare.com/files/50360895"

# Mapping: sheet name → (output_name, item base names)
SHEETS = {
    "Language Skills": (
        "cano_villagrasa_2024_language_skills",
        [
            "Sentence Comprehension",
            "Linguistic Concepts",
            "Morphosyntax",
            "Pragmatic Skills Profile",
            "Oral Text Comprehension",
        ],
    ),
    "Cognitive Competence": (
        "cano_villagrasa_2024_cognitive_competence",
        [
            "Verbal Comprehension",
            "Visuospatial",
            "Fluid Reasoning",
            "Working Memory",
            "Processing Speed",
        ],
    ),
    "Executive Functions": (
        "cano_villagrasa_2024_executive_functions",
        [
            "Interference Resistance",
            "Trail Making",
            "Verbal Fluency",
            "Ring Construction",
        ],
    ),
}

GROUP_SUFFIX_DYSLEXIA = "_G-DYSLEXIA"
GROUP_SUFFIX_CONTROL = "_G-CONTROL"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    r = requests.get(DATA_URL, headers=HEADERS)
    r.raise_for_status()
    xl = pd.ExcelFile(io.BytesIO(r.content))

    for sheet_name, (out_name, item_bases) in SHEETS.items():
        df = xl.parse(sheet_name)

        # Build a long dataframe with two rows per matched pair (one dyslexia, one control)
        records = []
        for _, row in df.iterrows():
            pair_id = int(row["Participant ID"])
            id_dyslexia = pair_id * 2 - 1
            id_control = pair_id * 2

            for base in item_bases:
                col_dys = f"{base}{GROUP_SUFFIX_DYSLEXIA}"
                col_ctrl = f"{base}{GROUP_SUFFIX_CONTROL}"

                # Clean item name: lowercase, underscores
                item_name = base.lower().replace(" ", "_")

                records.append({
                    "id": id_dyslexia,
                    "item": item_name,
                    "resp": row[col_dys],
                    "treat": 1,
                })
                records.append({
                    "id": id_control,
                    "item": item_name,
                    "resp": row[col_ctrl],
                    "treat": 0,
                })

        long = pd.DataFrame(records)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        # Enforce column order: id, item, resp, treat
        long = long[["id", "item", "resp", "treat"]]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(
            f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
            f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
        )


if __name__ == "__main__":
    convert()
