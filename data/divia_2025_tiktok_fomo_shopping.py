"""
Processing script for: TikTok / FoMO Shopping Behavior (Indonesia)
Source: https://figshare.com/articles/dataset/Data_Support_-_Digital_Shopping_Behavior_among_Indonesian_TikTok_Users_Exploring_Livestream_Shopping_and_Fear_of_Missing_Out/29378996
DOI: 10.6084/m9.figshare.29378996.v2
License: CC-BY 4.0
N = 400 participants, 21 items, 5-point Likert scale
Author/year: Divia 2025
Scale prefixes:
  UP  = Utilitarian Purchase (3 items: UP1-UP3)
  KI  = Consumer/Purchase Intention (3 items: KI1-KI3)
  LP  = Livestream Purchase (2 items: LP1-LP2)
  R   = Review/Recommendation (3 items: R1-R3)
  T   = Trust (2 items: T1-T2)
  PP  = Purchase Promotion (2 items: PP1-PP2)
  PM  = Price/Monetary (2 items: PM1-PM2)
  EP  = Emotional Purchase (2 items: EP1-EP2)
  MP  = Missing Out Purchase / FoMO (2 items: MP1-MP2)
All items kept in a single file (one scale study, items measure related constructs).
"""

import requests
import pandas as pd
import os

OUTPUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Download data
UA = {"User-Agent": "irw-discovery-scout/1.0"}
r = requests.get("https://api.figshare.com/v2/articles/29378996", headers=UA)
files = r.json()["files"]
dl_url = next(f["download_url"] for f in files if "Divia" in f["name"])
data = requests.get(dl_url, headers=UA)

tmp_path = "/tmp/divia_2025_tiktok_fomo_shopping_raw.xlsx"
with open(tmp_path, "wb") as f:
    f.write(data.content)

# Load
df = pd.read_excel(tmp_path, sheet_name="data")

# Item columns
item_cols = [
    "UP1", "UP2", "UP3",
    "KI1", "KI2", "KI3",
    "LP1", "LP2",
    "R1", "R2", "R3",
    "T1", "T2",
    "PP1", "PP2",
    "PM1", "PM2",
    "EP1", "EP2",
    "MP1", "MP2",
]
assert len(item_cols) == 21, f"Expected 21 item columns"

# Create person id from row index (Username TikTok is not always unique and may contain PII)
# Use 1-based integer id
df["id"] = range(1, len(df) + 1)

# Covariate columns
# Jenis Kelamin = gender, Usia = age, Pendidikan = education,
# Domisili = location, Penghasilan = income, Brand = brand surveyed
cov_rename = {
    "Jenis Kelamin": "cov_gender",
    "Usia": "cov_age",
    "Pendidikan": "cov_education",
    "Domisili": "cov_location",
    "Penghasilan": "cov_income",
    "Brand": "cov_brand",
}
df = df.rename(columns=cov_rename)

# Melt to long format
id_vars = ["id"] + list(cov_rename.values())
df_long = df.melt(
    id_vars=id_vars,
    value_vars=item_cols,
    var_name="item",
    value_name="resp",
)

# Sort
df_long = df_long.sort_values(["id", "item"]).reset_index(drop=True)

# Validate
assert df_long["resp"].between(1, 5).all(), "Responses outside 1-5 range"
assert df_long["resp"].isna().sum() == 0, "Unexpected NA values in resp"
assert df_long["id"].nunique() == 400, f"Expected 400 participants, got {df_long['id'].nunique()}"
assert len(df_long) == 400 * 21, f"Expected {400*21} rows, got {len(df_long)}"

print(f"N participants: {df_long['id'].nunique()}")
print(f"N items: {df_long['item'].nunique()}")
print(f"N rows: {len(df_long)}")
print(f"Response range: {df_long['resp'].min()} - {df_long['resp'].max()}")
print(f"Columns: {list(df_long.columns)}")

# Save
out_path = os.path.join(OUTPUT_DIR, "divia_2025_tiktok_fomo_shopping.csv")
df_long.to_csv(out_path, index=False)
print(f"Saved to {out_path}")
