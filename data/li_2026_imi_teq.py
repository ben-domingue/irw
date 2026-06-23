"""
Processing script for:
Li, Su & Wang (2026)
"Chinese IMI-TEQ: Cross-Cultural Adaptation and Psychometric Evaluation
 in the Context of Modeling Software Learning"
Figshare: https://doi.org/10.6084/m9.figshare.32766447.v1
License: CC BY 4.0

The IMI-TEQ (Intrinsic Motivation Inventory - Technology Enhanced Questionnaire)
contains 34 items across subscales:
  - Items 1-7:   Intrinsic Motivation / Enjoyment
  - Items 8-12:  Perceived Competence
  - Items 13-17: Perceived Choice / Autonomy
  - Items 18-22: Pressure / Tension (Anxiety)
  - Items 23-32: Epistemic Curiosity / Fulfillment
  - Items 33-34: System Usability (TEQ-specific items)

All 34 items are processed as a single IRW output file (all measure the
same instrument and 7-point Likert scale).
"""

import os
import requests
import pandas as pd

RAW_URL = "https://ndownloader.figshare.com/files/65776596"
RAW_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/raw_downloads"
RAW_FILE = os.path.join(RAW_DIR, "imi_teq_chinese.xlsx")
OUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# Download if not already present
if not os.path.exists(RAW_FILE):
    r = requests.get(RAW_URL, headers={"User-Agent": "irw-discovery-scout/1.0"})
    with open(RAW_FILE, "wb") as f:
        f.write(r.content)

# Load
df = pd.read_excel(RAW_FILE, sheet_name="Sheet1")

# Identify item columns: all columns except the 4 covariate/ID columns
meta_cols = ["ID", "Gender", "Region", "Use experience"]
item_cols = [c for c in df.columns if c not in meta_cols]

# Rename to IRW schema
df = df.rename(columns={
    "ID": "id",
    "Gender": "cov_gender",
    "Region": "cov_region",
    "Use experience": "cov_use_experience",
})

# Create shorter item names: extract leading number from each column name
# e.g. "1.While I was working..." -> "item_01"
def make_item_name(col):
    # Extract the leading number
    import re
    m = re.match(r'^(\d+)[\.\s]', col.strip())
    if m:
        return f"item_{int(m.group(1)):02d}"
    return col

item_rename = {col: make_item_name(col) for col in item_cols}
df = df.rename(columns=item_rename)
item_cols_renamed = [item_rename[c] for c in item_cols]

# Pivot to long format
cov_cols = ["cov_gender", "cov_region", "cov_use_experience"]
id_vars = ["id"] + cov_cols

long = df[id_vars + item_cols_renamed].melt(
    id_vars=id_vars,
    value_vars=item_cols_renamed,
    var_name="item",
    value_name="resp",
)
long = long.dropna(subset=["resp"])
long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
long = long.dropna(subset=["resp"])
long["id"] = long["id"].astype(int)

out_path = os.path.join(OUT_DIR, "li_2026_imi_teq.csv")
long.to_csv(out_path, index=False)
print(f"Saved {out_path}")
print(f"  Participants: {long['id'].nunique()}")
print(f"  Items: {long['item'].nunique()}")
print(f"  Response range: [{long['resp'].min()}, {long['resp'].max()}]")
print(f"  Total rows: {len(long)}")
print("Done.")
