"""
Depression Anxiety and Stress Data (DASS-21 variant)
Source: https://doi.org/10.7910/DVN/TAISB2  (Harvard Dataverse)

21 items (Q1-Q21), 0-4 response scale. Item text not in data file.
9 person-level covariates extracted; all are categorical and numerically coded
(codebook needed to interpret categories).

NOTE: resp scale is 0-4 (not the standard DASS-21 0-3) — verify instrument
and coding before submission.
"""

import os
import pandas as pd

QUEUE_FILE = "../automated_finding/irw_output/queue/10_7910_dvn_taisb2.csv"
OUT_DIR    = "../automated_finding/irw_output/cleaned"

def update_index(out_dir, rows):
    """Upsert rows into cleaned_index.csv (keyed on 'file'), one level above cleaned/."""
    idx_path = os.path.join(os.path.dirname(out_dir), "cleaned_index.csv")
    cols = ["file","doi","title","scale","n_participants","n_items",
            "n_responses","resp_range","license","notes","status"]
    if os.path.exists(idx_path):
        idx = pd.read_csv(idx_path)
    else:
        idx = pd.DataFrame(columns=cols)
    new_files = {r["file"] for r in rows}
    idx = idx[~idx["file"].isin(new_files)]
    idx = pd.concat([idx, pd.DataFrame(rows)], ignore_index=True)
    idx[cols].to_csv(idx_path, index=False)

COV_MAP = {
    "Age ":                  "cov_age",
    "Sex":                   "cov_sex",
    "Education ":            "cov_education",
    "Experience ":           "cov_experience",
    "Monthly income ":       "cov_monthly_income",
    "Marital status ":       "cov_marital_status",
    "Weekly working hours ": "cov_weekly_working_hours",
    "Smoking ":              "cov_smoking",
    "Caffeine ":             "cov_caffeine",
}

os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(QUEUE_FILE)

# Build covariate table
cov_long = df[df["item"].isin(COV_MAP)].copy()
cov_long["cov_col"] = cov_long["item"].map(COV_MAP)
covs = cov_long.pivot_table(index="id", columns="cov_col", values="resp", aggfunc="first").reset_index()

# Item response rows
items_df = df[~df["item"].isin(COV_MAP)].copy()
items_df["item"] = items_df["item"].str.strip().str.lower()   # q1, q2, ...

out_df = items_df.merge(covs, on="id", how="left")
out_df = out_df.sort_values(["id", "item"]).reset_index(drop=True)

out = os.path.join(OUT_DIR, "dass21_depression_anxiety_stress.csv")
out_df.to_csv(os.path.join(OUT_DIR, "dass21_depression_anxiety_stress.csv"), index=False)
print(f"DASS-21 variant: {out_df['id'].nunique()} participants, {out_df['item'].nunique()} items, {len(out_df)} rows")
print(f"Resp range: {sorted(out_df['resp'].dropna().unique())}")

update_index(OUT_DIR, [
    {"file": "dass21_depression_anxiety_stress.csv",
     "doi": "10.7910/DVN/TAISB2", "title": "Depression Anxiety and Stress Data",
     "scale": "DASS-21 variant", "n_participants": out_df["id"].nunique(), "n_items": out_df["item"].nunique(),
     "n_responses": len(out_df), "resp_range": "0-4", "license": "cc0",
     "notes": "resp scale 0-4 (non-standard — verify instrument); covariate codes are numeric (codebook needed); item text absent (Q1-Q21 only)",
     "status": "cleaned"},
])
