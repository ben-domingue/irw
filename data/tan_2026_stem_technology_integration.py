"""
Dataset: Science Teacher's Belief, Attitude, and Practice of Technology Integration in STEM Education
Source: https://figshare.com/articles/dataset/Science_Teacher_s_Belief_Attitude_and_Practice_of_Technology_Integration_in_STEM_Education/32024295
DOI: 10.6084/m9.figshare.32024295.v1
Author: ShuYuan Tan
Published: 2026
License: CC BY
N: 80 participants
Items: 15 (Likert 1-5)
Covariates: gender, degree, subject, age (categorical)
"""

import requests
import io
import pandas as pd
import os

UA = {"User-Agent": "irw-discovery-scout/1.0"}
OUTPUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"

# Download from figshare
url = "https://ndownloader.figshare.com/files/63759105"
raw = requests.get(url, headers=UA).content
df = pd.read_excel(io.BytesIO(raw), sheet_name="Form Responses 1")

# Create person ID from row index (no explicit participant ID in data)
df = df.reset_index(drop=True)
df["id"] = df.index + 1

# Rename covariates
df = df.rename(columns={
    "Gender": "cov_gender",
    "Degree ": "cov_degree",
    "Subject": "cov_subject",
    "Age": "cov_age",
})

# Identify item columns (numbered question text columns)
item_cols = [c for c in df.columns if c[:1].isdigit()]

# Create short item labels: item_01 ... item_15
item_map = {col: f"item_{i+1:02d}" for i, col in enumerate(item_cols)}

df_items = df.rename(columns=item_map)
short_item_cols = list(item_map.values())

cov_cols = ["cov_gender", "cov_degree", "cov_subject", "cov_age"]

long = df_items[["id"] + cov_cols + short_item_cols].melt(
    id_vars=["id"] + cov_cols,
    value_vars=short_item_cols,
    var_name="item",
    value_name="resp",
)
long = long.dropna(subset=["resp"])
long["resp"] = long["resp"].astype(int)
long = long.sort_values(["id", "item"]).reset_index(drop=True)

out_path = os.path.join(OUTPUT_DIR, "tan_2026_stem_technology_integration.csv")
long.to_csv(out_path, index=False)
print(f"Wrote {out_path}: {long.shape[0]} rows, {long['id'].nunique()} persons, "
      f"{long['item'].nunique()} items, resp range {long['resp'].min()}-{long['resp'].max()}")
