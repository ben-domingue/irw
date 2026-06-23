#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/U6YTI5
# DOI: 10.7910/dvn/u6yti5
# License: CC0
# Dataset: Roadmaps to Representation — expert survey of SF political experts
# 39 participants rating SF political candidates/organizations on 3 question sets:
#   q2_*: vote choice ranking (1-11 scale, 6 candidates)
#   q4_*: ideology rating (1-7 scale, 14 candidates/orgs)
#   q6_*: ideology rating (1-7 scale, 14 candidates/orgs)
# 99 = sentinel for "don't know / not applicable"

import os
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID = 3176965  # expert_1.xlsx
URL = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    resp = requests.get(URL, headers=HEADERS)
    resp.raise_for_status()

    from io import BytesIO
    df = pd.read_excel(BytesIO(resp.content))

    # id column already named 'id'
    # Covariates: ideo (expert's own ideology, 1-7 + 99 sentinel), sf_pols (familiarity)
    df = df.rename(columns={
        "ideo": "cov_ideo",
        "sf_pols": "cov_sf_pols",
    })
    # Filter sentinel 99 from covariates
    df["cov_ideo"] = df["cov_ideo"].where(df["cov_ideo"] != 99, other=None)
    df["cov_sf_pols"] = df["cov_sf_pols"].where(df["cov_sf_pols"] != 99, other=None)

    cov_cols = ["cov_ideo", "cov_sf_pols"]

    # Drop start/end/sf_pols_other columns (not item responses)
    q2_cols = [c for c in df.columns if c.startswith("q2_")]
    q4_cols = [c for c in df.columns if c.startswith("q4_")]
    q6_cols = [c for c in df.columns if c.startswith("q6_")]

    SCALES = {
        "mcdermott_2014_roadmaps_vote_ranking.csv": (q2_cols, 1, 11),
        "mcdermott_2014_roadmaps_ideology_q4.csv": (q4_cols, 1, 7),
        "mcdermott_2014_roadmaps_ideology_q6.csv": (q6_cols, 1, 7),
    }

    for out_name, (item_cols, vmin, vmax) in SCALES.items():
        long = df[["id"] + cov_cols + item_cols].melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp"
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # Filter sentinel 99
        long = long[(long["resp"] >= vmin) & (long["resp"] <= vmax)].reset_index(drop=True)

        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(os.path.join(OUT_DIR, out_name), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
