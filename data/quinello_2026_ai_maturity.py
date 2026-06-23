"""
IRW processing script: AI Technological Maturity in Facilities Management

Source: Robson Quinello (2026)
DOI: 10.6084/m9.figshare.32714616.v1
URL: https://figshare.com/articles/dataset/32714616
License: CC BY 4.0

Data: 104 participants, 21 items across 2 sub-scales
Sub-scales:
  - Maturity dimensions (14 items, 1-7 Likert):
      DATA, INFR, MATU, STS, TI, CULT, LEAD, STRA, EXTE, INVE, GOVE, SKILL, STAK, USER
  - AI technology adoption (7 items, 0-6 scale):
      CV, NLP, ES, ML, RB, PLT, VCT
Covariates:
  - cov_experience (Years of experience)
  - cov_position (Current position)
  - cov_education (Educational background)
  - cov_origin (National/Foreign)
  - cov_sector (Sector)
  - cov_company_size (Company size)

Note: TML_M is a computed mean column — excluded from item-level output.

Output files (long format, one per sub-scale):
  quinello_2026_ai_maturity_dimensions.csv
  quinello_2026_ai_maturity_technology.csv
"""

import requests
import io
import pandas as pd
import os

UA = {"User-Agent": "irw-discovery-scout/1.0"}
OUTPUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"

# Download from figshare
meta = requests.get("https://api.figshare.com/v2/articles/32714616", headers=UA).json()
file_info = meta["files"][0]
raw = requests.get(file_info["download_url"], headers=UA).content
df = pd.read_excel(io.BytesIO(raw))

# Rename covariate columns (strip trailing spaces)
df = df.rename(columns={
    "Years of experience ": "cov_experience",
    "Current position ": "cov_position",
    "Educational background": "cov_education",
    "Origin": "cov_origin",
    "Sector": "cov_sector",
    "Company size": "cov_company_size",
})

cov_cols = ["cov_experience", "cov_position", "cov_education", "cov_origin", "cov_sector", "cov_company_size"]

# Sub-scale 1: AI maturity dimensions (14 items, Likert 1-7)
dim_items = ["DATA", "INFR", "MATU", "STS", "TI", "CULT", "LEAD", "STRA", "EXTE", "INVE", "GOVE", "SKILL", "STAK", "USER"]

long_dim = df[["Case"] + cov_cols + dim_items].copy()
long_dim = long_dim.rename(columns={"Case": "id"})
long_dim = long_dim.melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
long_dim = long_dim.sort_values(["id", "item"]).reset_index(drop=True)

out_dim = os.path.join(OUTPUT_DIR, "quinello_2026_ai_maturity_dimensions.csv")
long_dim.to_csv(out_dim, index=False)
print(f"Wrote {out_dim}: shape={long_dim.shape}, resp range=[{long_dim['resp'].min()},{long_dim['resp'].max()}]")

# Sub-scale 2: AI technology adoption (7 items, 0-6 scale)
tech_items = ["CV", "NLP", "ES", "ML", "RB", "PLT", "VCT"]

long_tech = df[["Case"] + cov_cols + tech_items].copy()
long_tech = long_tech.rename(columns={"Case": "id"})
long_tech = long_tech.melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
long_tech = long_tech.sort_values(["id", "item"]).reset_index(drop=True)

out_tech = os.path.join(OUTPUT_DIR, "quinello_2026_ai_maturity_technology.csv")
long_tech.to_csv(out_tech, index=False)
print(f"Wrote {out_tech}: shape={long_tech.shape}, resp range=[{long_tech['resp'].min()},{long_tech['resp'].max()}]")
