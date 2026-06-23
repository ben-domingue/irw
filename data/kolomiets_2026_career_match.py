"""
Processing script for: JobCannon Psychometric Response Dataset (career_match)
Author: Peter Kolomiets (JobCannon)
Year: 2026
Source DOI: 10.6084/m9.figshare.32668833.v1
License: CC BY 4.0
Instrument: Mini-RIASEC forced-choice career interest (12 items, 0-5 scale)
N participants: 2005, N items: 12

Notes:
- One row (id=1139) had JSON-encoded item values ({"value": N, "question_index": N});
  the numeric value is extracted.
- q8 has one out-of-range value (7) and q11 has one out-of-range value (8); these are
  retained as-is (expected scale is 0-5).
- Covariates included: locale, duration_seconds, top_result, and 6 RIASEC scores.
"""

import json
import os
import pandas as pd

RAW_PATH = "/home/ben/Dropbox/projects/irw/src/automated_finding/raw_data/career_match.csv"
OUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"
OUT_NAME = "kolomiets_2026_career_match"

# Load
d = pd.read_csv(RAW_PATH)

# Item columns
item_cols = [c for c in d.columns if c.startswith("q")]

# Parse values: most are plain integers; one row has JSON-encoded objects
def parse_val(v):
    v = str(v)
    if v.startswith("{"):
        return json.loads(v)["value"]
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None

for col in item_cols:
    d[col] = d[col].apply(parse_val)

# Rename covariates
d = d.rename(columns={
    "locale": "cov_locale",
    "duration_seconds": "cov_duration_seconds",
    "top_result": "cov_top_result",
    "score_A": "cov_score_A",
    "score_C": "cov_score_C",
    "score_E": "cov_score_E",
    "score_I": "cov_score_I",
    "score_R": "cov_score_R",
    "score_S": "cov_score_S",
})

# Keep id + covariates + items for melt
cov_cols = [c for c in d.columns if c.startswith("cov_")]
keep_cols = ["id"] + cov_cols + item_cols
d = d[keep_cols]

# Pivot to long format
d_long = pd.melt(d, id_vars=["id"] + cov_cols, value_vars=item_cols,
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
