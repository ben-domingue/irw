"""
Dataset: Foreign Language Proficiency, Academic Identity and Dissonance
Source: https://springernature.figshare.com/articles/dataset/Additional_file_7_of_Beyond_translation_a_quantitative_study_on_foreign_language_proficiency_academic_identity_and_dissonance_among_educational_researchers/31387864
DOI: 10.6084/m9.figshare.31387864.v1
Authors: Mohamed Mekheimer, Walid Abdelhalim
Published: 2026
License: CC BY
N: 160 participants
Scales:
  FLP  - Foreign Language Proficiency (4 items, 1-5 scale)
  PAF  - Professional Academic Functioning (10 items, 1-7 scale)
  CAI  - Cultural Academic Identity (18 items, 1-5 scale)
  ID   - Identity Dissonance (10 items, 1-7 scale)
"""

import requests
import io
import pandas as pd
import os

UA = {"User-Agent": "irw-discovery-scout/1.0"}
OUTPUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"

# Download from figshare
url = "https://ndownloader.figshare.com/files/62067259"
raw = requests.get(url, headers=UA).content
df = pd.read_excel(io.BytesIO(raw), sheet_name="survey_data (1)")

# Rename person ID
df = df.rename(columns={
    "Participant_ID": "id",
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Field": "cov_field",
})

# Define scales
scales = {
    "flp": [c for c in df.columns if c.startswith("FLP_")],
    "paf": [c for c in df.columns if c.startswith("PAF_")],
    "cai": [c for c in df.columns if c.startswith("CAI_")],
    "id":  [c for c in df.columns if c.startswith("ID_")],
}

cov_cols = ["cov_age", "cov_gender", "cov_field"]

for scale_name, item_cols in scales.items():
    long = df[["id"] + cov_cols + item_cols].melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    out_name = f"mekheimer_2026_{scale_name}.csv"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    long.to_csv(out_path, index=False)
    print(f"Wrote {out_path}: {long.shape[0]} rows, {long['id'].nunique()} persons, "
          f"{long['item'].nunique()} items, resp range {long['resp'].min()}-{long['resp'].max()}")
