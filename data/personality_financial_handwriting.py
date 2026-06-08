"""
Personality, Financial Behaviour, and Handwriting Analysis
Source: https://doi.org/10.7910/DVN/2IBLRK  (Harvard Dataverse)

402 participants. Two scales:
  1. graphology — 25 binary (0/1) handwriting feature ratings
  2. financial_behavior — 12 Likert items (mostly 1-5) on financial attitudes/personality
"""

import os
import pandas as pd

QUEUE_FILE = "../automated_finding/irw_output/queue/10_7910_dvn_2iblrk.csv"
OUT_DIR    = "../automated_finding/irw_output/cleaned"
DOI        = "10.7910/DVN/2IBLRK"
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

BINARY_ITEMS = {
    "Arcade", "Capital Letter – Tall and Narrow", "Depression valley",
    "Encircled signature", "Erratic slant", "Extreme Right slant",
    "Heavy slashing storkes", "Lack of Symmetry in zones",
    "Miniature size letters", "Narrow left, wide right margins", "Rapid movement ",
    "Retraced letter d and t. Sharp and angular retracement ",
    "Signature extreme right", "Small mid zone with long upper and lower zone loops",
    "Small size (middle zone)", "Sudden change in speed, size, and pressure",
    "T cross to right", "Tightly closed A and O", "Too angular, devoid of roundedness ",
    "Unfinished down stroke", "Varying or eratic slant", "Wavy baselines",
    "Wide left margin", "i and j dots dashed and rigth to the stem",
    "‘M’ lower loops- larger the loops more the worry",
}

LIKERT_ITEMS = {
    "A penny saved is a penny earned ",
    "I am often full of doubts and fears",
    "I am unhappy if people don't respond to my email/ social media message",
    "I believe that earning a salary gives a more secured source of income",
    "I invest in financial instruments with guaranteed returns",
    "I keep changing my plans",
    "I keep on postponing my financial decisions",
    "I often take loans to finance my spending  ",
    "I rarely discuss my incomes with others",
    "I value having a lot of easy-to-access money in the bank",
    "I want to perform my own investment research instead of seeking advice",
    "My thoughts are more controlled than emotional",
}

# --- Graphology scale (binary 0/1) ---
graph_df = df[df["item"].isin(BINARY_ITEMS)].copy()
graph_df["item"] = graph_df["item"].str.strip()
graph_df["resp"] = graph_df["resp"].astype(int)
graph_df = graph_df.sort_values(["id", "item"]).reset_index(drop=True)

out_graph = "personality_financial_handwriting__graphology.csv"
graph_df.to_csv(os.path.join(OUT_DIR, out_graph), index=False)
print(f"graphology: {graph_df['id'].nunique()} participants, "
      f"{graph_df['item'].nunique()} items, {len(graph_df)} rows")

# --- Financial behavior/personality scale (Likert 1-5) ---
fin_df = df[df["item"].isin(LIKERT_ITEMS)].copy()
fin_df["item"] = fin_df["item"].str.strip()
fin_df["resp"] = fin_df["resp"].astype(int)
fin_df = fin_df.sort_values(["id", "item"]).reset_index(drop=True)

out_fin = "personality_financial_handwriting__financial_behavior.csv"
fin_df.to_csv(os.path.join(OUT_DIR, out_fin), index=False)
print(f"financial_behavior: {fin_df['id'].nunique()} participants, "
      f"{fin_df['item'].nunique()} items, {len(fin_df)} rows")
print(f"Resp range: {sorted(fin_df['resp'].unique())}")

update_index(OUT_DIR, [
    {"file": out_graph,
     "doi": DOI, "title": "Personality, Financial Behaviour, and Handwriting Analysis",
     "scale": "graphology", "n_participants": graph_df["id"].nunique(),
     "n_items": graph_df["item"].nunique(), "n_responses": len(graph_df),
     "resp_range": "0-1", "license": LICENSE,
     "notes": "binary handwriting feature ratings by expert examiner; item text = feature name",
     "status": "cleaned"},
    {"file": out_fin,
     "doi": DOI, "title": "Personality, Financial Behaviour, and Handwriting Analysis",
     "scale": "financial_behavior", "n_participants": fin_df["id"].nunique(),
     "n_items": fin_df["item"].nunique(), "n_responses": len(fin_df),
     "resp_range": "0-5", "license": LICENSE,
     "notes": "mixed financial attitude and personality Likert items; item text = item label",
     "status": "cleaned"},
])
