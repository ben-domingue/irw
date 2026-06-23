"""
Dataset: Aggregated response information from all 78 students to the questionnaire
DOI: 10.1371/journal.pone.0340806.s001
Figshare: https://plos.figshare.com/articles/dataset/31091356
License: CC-BY 4.0
N = 78 students / 15 items

Despite the "aggregated" title, inspection confirms each row is one individual student
(No = 1..78, integer Likert responses 3-5 on a 1-5 scale, no fractional values).
Single scale: Q1–Q15 (student questionnaire items).
"""

import requests
import io
import os
import pandas as pd

UA = {"User-Agent": "irw-discovery-scout/1.0"}
OUTPUT_DIR = "/home/ben/Dropbox/projects/irw/src/automated_finding/irw_output/cleaned"

# Download
meta = requests.get("https://api.figshare.com/v2/articles/31091356", headers=UA).json()
files = meta.get("files", [])
f = next(x for x in files if ".xlsx" in x["name"].lower())
raw = requests.get(f["download_url"], headers=UA).content
df = pd.read_excel(io.BytesIO(raw))

# 'No' is the participant ID (1-78)
df = df.rename(columns={"No": "id"})

# Item columns: Q1–Q15
item_cols = [c for c in df.columns if c.startswith("Q")]

# Melt to long format
long_df = df[["id"] + item_cols].melt(
    id_vars=["id"], var_name="item", value_name="resp"
)

out_path = os.path.join(OUTPUT_DIR, "alomari_2025_student_questionnaire.csv")
long_df.to_csv(out_path, index=False)
print(f"Saved alomari_2025_student_questionnaire.csv — {long_df.shape[0]} rows, "
      f"{long_df['id'].nunique()} participants, {long_df['item'].nunique()} items")
print("Done.")
