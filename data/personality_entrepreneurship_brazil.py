"""
Personality and Entrepreneurship in Brazil
Source: https://doi.org/10.7910/DVN/IEK9PW  (Harvard Dataverse)

340 participants. Five scales (4 items each, 1-5 Likert):
  1. abex  — Ability to Export (ABEX1-4)
  2. con   — Conscientiousness (CON1-4)
  3. ex    — Extraversion (EX1-4)
  4. inem  — Entrepreneurial Motivation (INEM1-4)
  5. neu   — Neuroticism (NEU1-4)
Covariates: EDU (education, 1-5), NEGPRO (negative profit outcome, 0/1).

DOI: 10.7910/DVN/IEK9PW
License: CC0
"""

import os
import pandas as pd

QUEUE_FILE = "../automated_finding/irw_output/queue/10_7910_dvn_iek9pw.csv"
OUT_DIR    = "../automated_finding/irw_output/cleaned"
DOI        = "10.7910/DVN/IEK9PW"
LICENSE    = "cc0"


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

SCALES = {
    "abex": ["ABEX1", "ABEX2", "ABEX3", "ABEX4"],
    "con":  ["CON1",  "CON2",  "CON3",  "CON4"],
    "ex":   ["EX1",   "EX2",   "EX3",   "EX4"],
    "inem": ["INEM1", "INEM2", "INEM3", "INEM4"],
    "neu":  ["NEU1",  "NEU2",  "NEU3",  "NEU4"],
}

SCALE_TITLES = {
    "abex": "Personality and Entrepreneurship (Brazil) — Ability to Export",
    "con":  "Personality and Entrepreneurship (Brazil) — Conscientiousness",
    "ex":   "Personality and Entrepreneurship (Brazil) — Extraversion",
    "inem": "Personality and Entrepreneurship (Brazil) — Entrepreneurial Motivation",
    "neu":  "Personality and Entrepreneurship (Brazil) — Neuroticism",
}

COV_ITEMS = {"EDU", "NEGPRO"}

# Build per-participant covariate table
cov_long = df[df["item"].isin(COV_ITEMS)].copy()
covs = cov_long.pivot_table(index="id", columns="item", values="resp", aggfunc="first")
covs = covs.rename(columns={"EDU": "cov_education", "NEGPRO": "cov_neg_profit"})
covs = covs.reset_index()

index_rows = []

for scale_name, item_names in SCALES.items():
    scale_df = df[df["item"].isin(item_names)].copy()
    scale_df["item"] = scale_df["item"].str.lower()
    scale_df["resp"] = scale_df["resp"].astype(int)
    scale_df = scale_df.merge(covs, on="id", how="left")
    scale_df = scale_df.sort_values(["id", "item"]).reset_index(drop=True)

    out_file = f"personality_entrepreneurship_brazil__{scale_name}.csv"
    scale_df.to_csv(os.path.join(OUT_DIR, out_file), index=False)

    n_p = scale_df["id"].nunique()
    n_i = scale_df["item"].nunique()
    n_r = len(scale_df)
    print(f"{scale_name}: {n_p} participants, {n_i} items, {n_r} rows")

    index_rows.append({
        "file": out_file,
        "doi": DOI,
        "title": SCALE_TITLES[scale_name],
        "scale": scale_name,
        "n_participants": n_p,
        "n_items": n_i,
        "n_responses": n_r,
        "resp_range": "1-5",
        "license": LICENSE,
        "notes": "item text not in data file; item names only (ABEX/CON/EX/INEM/NEU + number)",
        "status": "cleaned",
    })

update_index(OUT_DIR, index_rows)
print(f"\nSaved {len(index_rows)} scale files to {OUT_DIR}/")
