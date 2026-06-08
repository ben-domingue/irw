"""
Quarter-Life Crisis: Career Indecision, Intolerance of Uncertainty, Mental Well-Being
Source: https://doi.org/10.6084/m9.figshare.26130403.v1  (Figshare)

90 participants. Three scales:
  1. iuc  — Intolerance of Uncertainty Scale (IUS-12), 12 items, 1-5
  2. mwb  — Warwick-Edinburgh Mental Well-Being Scale (WEMWBS), 7 items, 1-5
  3. cd   — Career Decision Scale (modified), 18 items, 1-4
               (free-text items 3a, 6a, 16b, and item 19 excluded)

Item names derived from column positions in source file; item text available in Excel.

DOI: 10.6084/m9.figshare.26130403.v1
License: CC BY 4.0
"""

import os
import pandas as pd

QUEUE_FILE = "../automated_finding/irw_output/queue/10_6084_m9_figshare_26130403_v1.csv"
OUT_DIR    = "../automated_finding/irw_output/cleaned"
DOI        = "10.6084/m9.figshare.26130403.v1"
LICENSE    = "cc-by"


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

df = pd.read_csv(QUEUE_FILE)

# Column-name → clean item label mappings
# IU: col 13 (labelled 'INTOLERANCE OF UNCERTAINTY') through col 24 (Unnamed:14-24)
IUC_MAP = {
    "INTOLERANCE OF UNCERTAINTY": "iuc_1",
    "Unnamed: 14": "iuc_2",  "Unnamed: 15": "iuc_3",  "Unnamed: 16": "iuc_4",
    "Unnamed: 17": "iuc_5",  "Unnamed: 18": "iuc_6",  "Unnamed: 19": "iuc_7",
    "Unnamed: 20": "iuc_8",  "Unnamed: 21": "iuc_9",  "Unnamed: 22": "iuc_10",
    "Unnamed: 23": "iuc_11", "Unnamed: 24": "iuc_12",
}

# MWB: col 26 (labelled 'MENTAL WELL-BEING ') through col 32 (Unnamed:27-32)
MWB_MAP = {
    "MENTAL WELL-BEING ": "mwb_1",
    "Unnamed: 27": "mwb_2", "Unnamed: 28": "mwb_3", "Unnamed: 29": "mwb_4",
    "Unnamed: 30": "mwb_5", "Unnamed: 31": "mwb_6", "Unnamed: 32": "mwb_7",
}

# Career Decision: col 34 (labelled 'CAREER DECISION ') then cols 35,37-39,41-54 (Unnamed)
# Cols 36, 40, 52, 55 are free-text items and were excluded by the processing pipeline.
CD_MAP = {
    "CAREER DECISION ": "cd_1",
    "Unnamed: 35": "cd_2",   "Unnamed: 37": "cd_3b",  "Unnamed: 38": "cd_4",
    "Unnamed: 39": "cd_5",   "Unnamed: 41": "cd_6b",  "Unnamed: 42": "cd_7",
    "Unnamed: 43": "cd_8",   "Unnamed: 44": "cd_9",   "Unnamed: 45": "cd_10",
    "Unnamed: 46": "cd_11",  "Unnamed: 47": "cd_12",  "Unnamed: 48": "cd_13",
    "Unnamed: 49": "cd_14",  "Unnamed: 50": "cd_15",  "Unnamed: 51": "cd_16a",
    "Unnamed: 53": "cd_17",  "Unnamed: 54": "cd_18",
}

# AGE covariate (col 6)
AGE_ITEM = "Unnamed: 6"

SCALES = [
    ("iuc", IUC_MAP, "1-5",
     "Quarter-Life Crisis Study — Intolerance of Uncertainty Scale",
     "IUS-12; 12 items; item text available in Figshare Excel"),
    ("mwb", MWB_MAP, "1-5",
     "Quarter-Life Crisis Study — Mental Well-Being Scale",
     "WEMWBS; 7 items; item text available in Figshare Excel"),
    ("cd",  CD_MAP,  "1-4",
     "Quarter-Life Crisis Study — Career Decision Scale",
     "Career Decision Scale; 18 of 22 items (free-text 3a/6a/16b/19 excluded)"),
]

# Per-participant covariate: age
age_df = df[df["item"] == AGE_ITEM][["id", "resp"]].rename(columns={"resp": "cov_age"})

index_rows = []

for scale_name, item_map, resp_range, title, note in SCALES:
    scale_df = df[df["item"].isin(item_map)].copy()
    scale_df["item"] = scale_df["item"].map(item_map)
    scale_df["resp"] = scale_df["resp"].astype(int)
    scale_df = scale_df.merge(age_df, on="id", how="left")
    scale_df = scale_df.sort_values(["id", "item"]).reset_index(drop=True)

    out_file = f"quarter_life_crisis__{scale_name}.csv"
    scale_df.to_csv(os.path.join(OUT_DIR, out_file), index=False)

    n_p = scale_df["id"].nunique()
    n_i = scale_df["item"].nunique()
    n_r = len(scale_df)
    print(f"{scale_name}: {n_p} participants, {n_i} items, {n_r} rows, resp {resp_range}")

    index_rows.append({
        "file": out_file, "doi": DOI, "title": title, "scale": scale_name,
        "n_participants": n_p, "n_items": n_i, "n_responses": n_r,
        "resp_range": resp_range, "license": LICENSE,
        "notes": note, "status": "cleaned",
    })

update_index(OUT_DIR, index_rows)
print(f"\nSaved {len(index_rows)} scale files to {OUT_DIR}/")
