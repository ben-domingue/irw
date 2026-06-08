"""
Conspiracy Beliefs, Autistic Traits, and Schizotypy Study
Source: https://doi.org/10.6084/m9.figshare.30903575.v2  (Figshare)

433 participants. 5 scales extracted as separate IRW files:
  1. thinking_styles         — 10 items, 1-5
  2. cognitive_flexibility   — 20 items, 1-7
  3. asd_aq10                — 10 items, 1-4  (AQ-10 Autistic Traits)
  4. conspiracy_gcbs         — 15 items, 1-5  (Generic Conspiracy Beliefs Scale)
  5. schizotypy              — 37 items, 1-5

Demographics extracted as cov_* for each scale.

DOI: 10.6084/m9.figshare.30903575.v2
License: CC BY 4.0
"""

import io
import os
import re

import pandas as pd
import requests

FIGSHARE_URL = "https://ndownloader.figshare.com/files/60452459"
OUT_DIR      = "../automated_finding/irw_output/cleaned"
DOI          = "10.6084/m9.figshare.30903575.v2"
LICENSE      = "cc-by"


def update_index(out_dir, rows):
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


os.makedirs(OUT_DIR, exist_ok=True)

print("Downloading from Figshare...")
r = requests.get(FIGSHARE_URL, timeout=60)
r.raise_for_status()
raw = pd.read_excel(io.BytesIO(r.content), header=None)

# Row 0 = Qualtrics codes, row 1 = question text, rows 2+ = data
data = raw.iloc[2:].copy().reset_index(drop=True)
data.index = data.index + 1  # 1-based participant IDs
data.index.name = "id"
data = data.reset_index()

# ---------------------------------------------------------------------------
# Covariates (demographics, cols 9-20; skip free-text cols 12 and 15)
# ---------------------------------------------------------------------------
COV_COLS = {
    9:  "cov_gender",
    10: "cov_age",
    11: "cov_education",
    13: "cov_religiosity",
    14: "cov_religion",
    16: "cov_employed",
    17: "cov_job_satisfaction",
    18: "cov_life_satisfaction",
    19: "cov_relationship_satisfaction",
    20: "cov_political_orientation",
}
# +1 offset because data df has id as first column (so col index shifts by 1)
cov_df = data[["id"]].copy()
for col_idx, cov_name in COV_COLS.items():
    cov_df[cov_name] = pd.to_numeric(data.iloc[:, col_idx + 1], errors="coerce")

# ---------------------------------------------------------------------------
# Scale definitions: (name, col_range, prefix, resp_range)
# col_range uses original raw df column indices (before adding id column)
# ---------------------------------------------------------------------------
SCALES = [
    ("thinking_styles",       range(21, 31),  "ts",          "1-5"),
    ("cognitive_flexibility", range(32, 52),  "cfi",         "1-7"),
    ("asd_aq10",              range(53, 63),  "aq10",        "1-4"),
    ("conspiracy_gcbs",       range(64, 79),  "gcbs",        "1-5"),
    ("schizotypy",            range(80, 117), "schizotypy",  "1-5"),
]

TITLES = {
    "thinking_styles":       "Conspiracy Beliefs Study — Thinking Styles",
    "cognitive_flexibility": "Conspiracy Beliefs Study — Cognitive Flexibility Inventory",
    "asd_aq10":              "Conspiracy Beliefs Study — AQ-10 Autistic Traits",
    "conspiracy_gcbs":       "Conspiracy Beliefs Study — Generic Conspiracy Beliefs Scale",
    "schizotypy":            "Conspiracy Beliefs Study — Schizotypy",
}

index_rows = []

for scale_name, col_range, prefix, resp_range in SCALES:
    cols = list(col_range)
    n_items = len(cols)

    # Extract wide-format block; col indices into raw df (no id column yet)
    wide = data[["id"]].copy()
    for rank, col_idx in enumerate(cols, start=1):
        # data has id as col 0, then original cols shift by 1
        wide[f"{prefix}_{rank}"] = pd.to_numeric(data.iloc[:, col_idx + 1], errors="coerce")

    # Merge covariates
    wide = wide.merge(cov_df, on="id")

    # Melt to long format
    item_cols = [f"{prefix}_{i}" for i in range(1, n_items + 1)]
    cov_cols  = [c for c in wide.columns if c.startswith("cov_")]
    long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                     var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    fname = f"conspiracy_belief_schizotypy_asd__{scale_name}.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)

    n_participants = long["id"].nunique()
    n_responses    = len(long)
    print(f"{scale_name}: {n_participants} participants, {n_items} items, "
          f"{n_responses} responses, resp {resp_range}")

    index_rows.append({
        "file":          fname,
        "doi":           DOI,
        "title":         TITLES[scale_name],
        "scale":         scale_name,
        "n_participants": n_participants,
        "n_items":        n_items,
        "n_responses":    n_responses,
        "resp_range":     resp_range,
        "license":        LICENSE,
        "notes":          "item text available via Figshare docx; no reverse-coding applied",
        "status":         "cleaned",
    })

update_index(OUT_DIR, index_rows)
print(f"\nSaved {len(index_rows)} scale files to {OUT_DIR}/")
