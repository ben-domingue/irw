"""
Depression & Concussion-Like Symptoms in Adolescent Athletes
Source: https://doi.org/10.7910/DVN/5YF5XJ  (Harvard Dataverse)

Two scales in one file: PCSS (22 items, 0-6) and MFQ (33 items, 0-2).
Split into separate IRW files; demographics pulled out as cov_* columns.
"""

import os
import re
import pandas as pd

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

QUEUE_FILE  = "../automated_finding/irw_output/queue/10_7910_dvn_5yf5xj.csv"
OUT_DIR     = "../automated_finding/irw_output/cleaned"

COV_MAP = {
    "Age (Years) ":                   "cov_age",
    "Sex":                            "cov_sex",
    "Sport":                          "cov_sport",
    "Concussion History ":            "cov_concussion_history",
    "Concussion Number ":             "cov_concussion_number",
    "Learning Disability ":           "cov_learning_disability",
    "Anxiety Diagnosis ":             "cov_anxiety_diagnosis",
    "Anxiety Symptoms ":              "cov_anxiety_symptoms",
    "Depression Diagnosis ":          "cov_depression_diagnosis",
    "# of Prior Depressive Episodes ":"cov_prior_depressive_episodes",
    "Prior Depressive Episode(s) Y/N ":"cov_prior_depressive_episode_yn",
    "Aggregate Medical History":      "cov_aggregate_medical_history",
}

# Rows to drop (aggregate/summary scores, not item responses)
DROP_ITEMS = {
    "PCS Symptom Frequency (22) ",
    "PCS Symptom Severity (132) ",
    "MFQ 66",
    "MFQ Cut off ",
}


def normalize_item(name: str) -> str:
    """Standardize item labels: 'PCS12' -> 'pcss_12', 'MFQ 3' -> 'mfq_3'."""
    s = name.strip()
    m = re.match(r"PCS\s*(\d+)", s)
    if m:
        return f"pcss_{int(m.group(1))}"
    m = re.match(r"MFQ\s*(\d+)", s)
    if m:
        return f"mfq_{int(m.group(1))}"
    return s


df = pd.read_csv(QUEUE_FILE)

# --- Build covariate table (one row per id) ---
cov_long = df[df["item"].isin(COV_MAP)].copy()
cov_long["cov_col"] = cov_long["item"].map(COV_MAP)
cov_long["resp"] = cov_long["resp"].replace(-1, pd.NA)  # -1 is missing
covs = cov_long.pivot_table(index="id", columns="cov_col", values="resp", aggfunc="first")
covs = covs.reset_index()

# --- Item response rows only ---
items_df = df[~df["item"].isin(set(COV_MAP) | DROP_ITEMS)].copy()
items_df["item"] = items_df["item"].map(normalize_item)

# --- PCSS (Post-Concussion Symptom Scale, 22 items, 0-6) ---
import os
os.makedirs(OUT_DIR, exist_ok=True)

pcss = items_df[items_df["item"].str.startswith("pcss_")].merge(covs, on="id", how="left")
pcss = pcss.sort_values(["id", "item"]).reset_index(drop=True)
pcss.to_csv(os.path.join(OUT_DIR, "pcss_adolescent_athletes.csv"), index=False)
print(f"PCSS: {pcss['id'].nunique()} participants, {pcss['item'].nunique()} items, {len(pcss)} rows")

# --- MFQ (Mood and Feelings Questionnaire, 33 items, 0-2) ---
mfq = items_df[items_df["item"].str.startswith("mfq_")].merge(covs, on="id", how="left")
mfq = mfq.sort_values(["id", "item"]).reset_index(drop=True)
mfq.to_csv(os.path.join(OUT_DIR, "mfq_adolescent_athletes.csv"), index=False)
print(f"MFQ:  {mfq['id'].nunique()} participants, {mfq['item'].nunique()} items, {len(mfq)} rows")

update_index(OUT_DIR, [
    {"file": "pcss_adolescent_athletes.csv",
     "doi": "10.7910/DVN/5YF5XJ", "title": "Depression & Concussion-Like Symptoms in Adolescent Athletes",
     "scale": "PCSS", "n_participants": pcss["id"].nunique(), "n_items": pcss["item"].nunique(),
     "n_responses": len(pcss), "resp_range": "0-6", "license": "cc0",
     "notes": "resp direction unverified; item labels are numbered (pcss_1 through pcss_22)",
     "status": "cleaned"},
    {"file": "mfq_adolescent_athletes.csv",
     "doi": "10.7910/DVN/5YF5XJ", "title": "Depression & Concussion-Like Symptoms in Adolescent Athletes",
     "scale": "MFQ", "n_participants": mfq["id"].nunique(), "n_items": mfq["item"].nunique(),
     "n_responses": len(mfq), "resp_range": "0-2", "license": "cc0",
     "notes": "resp direction unverified; item labels are numbered (mfq_1 through mfq_33)",
     "status": "cleaned"},
])
