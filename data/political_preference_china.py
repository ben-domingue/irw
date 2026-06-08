"""
Self-reported Political Preference in China
Source: https://doi.org/10.7910/DVN/DWPLBC  (Harvard Dataverse)

392 participants. Three attitude items (0-5 ordinal) asking participants
to rate their views toward different online political factions.
Binary group-membership classifications and derived grouping variables
are excluded as they are not item responses.

DOI: 10.7910/DVN/DWPLBC
License: CC0
"""

import os
import pandas as pd

QUEUE_FILE = "../automated_finding/irw_output/queue/10_7910_dvn_dwplbc.csv"
OUT_DIR    = "../automated_finding/irw_output/cleaned"
DOI        = "10.7910/DVN/DWPLBC"
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

# The three attitude items — Chinese text, 0-5 ordinal
# 0=very negative, 5=very positive (inferred from context)
ATTITUDE_ITEMS = [
    "您对网络上亲自由主义立场的看法？",
    "您对持有“西方在文化和政治制度上都比中国更优秀”这一观点的群体的看法？",
    "您对网络上亲建制立场的看法？",
]

# Short English labels for each item
ITEM_LABELS = {
    "您对网络上亲自由主义立场的看法？":          "att_pro_liberal",
    "您对持有“西方在文化和政治制度上都比中国更优秀”这一观点的群体的看法？": "att_pro_western",
    "您对网络上亲建制立场的看法？":              "att_pro_establishment",
}

att_df = df[df["item"].isin(ATTITUDE_ITEMS)].copy()
att_df["item"] = att_df["item"].map(ITEM_LABELS)
att_df["resp"] = att_df["resp"].astype(int)
att_df = att_df.sort_values(["id", "item"]).reset_index(drop=True)

out_file = "political_preference_china.csv"
att_df.to_csv(os.path.join(OUT_DIR, out_file), index=False)
print(f"political_attitudes: {att_df['id'].nunique()} participants, "
      f"{att_df['item'].nunique()} items, {len(att_df)} rows")
print(f"Resp range: {sorted(att_df['resp'].unique())}")

update_index(OUT_DIR, [
    {"file": out_file,
     "doi": DOI,
     "title": "Self-reported Political Preference in China",
     "scale": "political_attitudes",
     "n_participants": att_df["id"].nunique(),
     "n_items": att_df["item"].nunique(),
     "n_responses": len(att_df),
     "resp_range": "0-5",
     "license": LICENSE,
     "notes": ("3-item attitude scale rating views toward online political factions; "
               "0=very negative, 5=very positive; item text in Chinese (see Dataverse)"),
     "status": "cleaned"},
])
