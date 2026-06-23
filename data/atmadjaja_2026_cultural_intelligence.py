"""
IRW processing script: Cultural Intelligence and Work Engagement (Gen Z, Multinationals)

Source: Stefanus Atmadjaja, reynard Lukman, Toto Edrinal Sebayang (2026)
DOI: 10.6084/m9.figshare.32747610.v1
URL: https://figshare.com/articles/dataset/32747610
License: CC BY 4.0

Data: 205 participants, 16 items across 4 scales (5-point Likert)
Scales:
  - CQ1-CQ4: Cultural Intelligence
  - POS1-POS4: Perceived Organizational Support
  - EWE1-EWE4: Employee Work Engagement
  - ITS1-ITS4: Intention to Stay

Output files (long format, one per scale):
  atmadjaja_2026_cultural_intelligence.csv
  atmadjaja_2026_pos.csv
  atmadjaja_2026_work_engagement.csv
  atmadjaja_2026_intention_to_stay.csv
"""

import requests
import io
import pandas as pd
import os

UA = {"User-Agent": "irw-discovery-scout/1.0"}
OUTPUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"

# Download from figshare
meta = requests.get("https://api.figshare.com/v2/articles/32747610", headers=UA).json()
file_info = meta["files"][0]
raw = requests.get(file_info["download_url"], headers=UA).content
df = pd.read_excel(io.BytesIO(raw))

# Person ID: use the "No." column (1-indexed respondent number)
# "Name" is anonymized ("Respondent 1", etc.) so not useful beyond No.

scales = {
    "cultural_intelligence": ["CQ1", "CQ2", "CQ3", "CQ4"],
    "pos": ["POS1", "POS2", "POS3", "POS4"],
    "work_engagement": ["EWE1", "EWE2", "EWE3", "EWE4"],
    "intention_to_stay": ["ITS1", "ITS2", "ITS3", "ITS4"],
}

for construct, item_cols in scales.items():
    long = df[["No."] + item_cols].copy()
    long = long.rename(columns={"No.": "id"})
    long = long.melt(id_vars="id", var_name="item", value_name="resp")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    out_path = os.path.join(OUTPUT_DIR, f"atmadjaja_2026_{construct}.csv")
    long.to_csv(out_path, index=False)
    print(f"Wrote {out_path}: shape={long.shape}, resp range=[{long['resp'].min()},{long['resp'].max()}]")
