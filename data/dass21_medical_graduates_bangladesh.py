"""
Depression Anxiety and Stress Among Medical Graduates in Bangladesh (DASS-21)
Source: https://doi.org/10.7910/DVN/NZ7VFL  (Harvard Dataverse)

Already in IRW long format with full item text. No covariates in item column.
DASS-21: 21 items, 0-3 response scale (0=did not apply, 3=applied very much).
"""

import os
import pandas as pd

QUEUE_FILE = "../automated_finding/irw_output/queue/10_7910_dvn_nz7vfl.csv"
OUT_DIR    = "../automated_finding/irw_output/cleaned"

def update_index(out_dir, rows):
    """Upsert rows into cleaned_index.csv (keyed on 'file')."""
    idx_path = os.path.join(out_dir, "cleaned_index.csv")
    cols = ["file","doi","title","scale","n_participants","n_items",
            "n_responses","resp_range","notes","status"]
    if os.path.exists(idx_path):
        idx = pd.read_csv(idx_path)
    else:
        idx = pd.DataFrame(columns=cols)
    new_files = {r["file"] for r in rows}
    idx = idx[~idx["file"].isin(new_files)]
    idx = pd.concat([idx, pd.DataFrame(rows)], ignore_index=True)
    idx[cols].to_csv(idx_path, index=False)

os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(QUEUE_FILE)

# Already clean — id, item (full text), resp (0-3). Just save.
df = df.sort_values(["id", "item"]).reset_index(drop=True)
df.to_csv(os.path.join(OUT_DIR, "dass21_medical_graduates_bangladesh.csv"), index=False)
print(f"DASS-21 Bangladesh: {df['id'].nunique()} participants, {df['item'].nunique()} items, {len(df)} rows")
print(f"Resp range: {sorted(df['resp'].dropna().unique())}")

update_index(OUT_DIR, [
    {"file": "dass21_medical_graduates_bangladesh.csv",
     "doi": "10.7910/DVN/NZ7VFL", "title": "Depression Anxiety and Stress Among Medical Graduates in Bangladesh",
     "scale": "DASS-21", "n_participants": df["id"].nunique(), "n_items": df["item"].nunique(),
     "n_responses": len(df), "resp_range": "0-3",
     "notes": "resp direction unverified; item text present",
     "status": "cleaned"},
])
