"""
Processing script for: Adoption of generative AI for instruction among CS teachers
Authors: Kang, Chunchen; Zhao, Shu
Year: 2024
Source DOI: 10.7910/DVN/8CE89H (Harvard Dataverse)
License: CC0
Instrument: Survey of AI adoption constructs for K-12 CS teachers in China
  - PE: Performance Expectancy (3 items)
  - EE: Effort Expectancy (2 items)
  - SI: Social Influence (3 items)
  - IE: Individual Efficacy (3 items)
  - CB: Cognitive Burden (3 items)
  - PR: Perceived Risk (3 items)
  - IU: Intention to Use (4 items)
  - AU: Actual Use (3 items)
  - BI: Behavioral Intention (3 items)
All items are 5-point Likert scale (1-5).
N participants: 338, N items: 27
"""

import os
import pandas as pd

RAW_PATH = "/home/ben/Dropbox/projects/irw/src/automated_finding/raw_data/ai_adoption_data.xlsx"
OUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"
OUT_NAME = "kang_2024_ai_adoption"

# Load
d = pd.read_excel(RAW_PATH)

# The first column '序号' is the participant sequence number (person ID)
d = d.rename(columns={"序号": "id"})

# All remaining columns are item responses (27 items)
item_cols = [c for c in d.columns if c != "id"]

# Pivot to long format
d_long = pd.melt(d, id_vars=["id"], value_vars=item_cols,
                 var_name="item", value_name="resp")

# Drop rows with missing responses
d_long = d_long.dropna(subset=["resp"])
d_long["resp"] = d_long["resp"].astype(int)

# Sort for cleanliness
d_long = d_long.sort_values(["id", "item"]).reset_index(drop=True)

print(f"Output shape: {d_long.shape}")
print(f"N unique participants: {d_long['id'].nunique()}")
print(f"N unique items: {d_long['item'].nunique()}")
print(f"Response range: {d_long['resp'].min()} - {d_long['resp'].max()}")
print(d_long.head())

# Save
os.makedirs(OUT_DIR, exist_ok=True)
out_csv = os.path.join(OUT_DIR, f"{OUT_NAME}.csv")
d_long.to_csv(out_csv, index=False)
print(f"Saved: {out_csv}")
