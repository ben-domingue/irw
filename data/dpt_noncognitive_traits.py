"""
Non-Cognitive Traits of Doctor of Physical Therapy (DPT) Learners
Source: https://doi.org/10.7910/DVN/Y75CP2  (Harvard Dataverse)

298 participants. Six scales:
  1. emotional_intelligence — Schutte EI Scale, 14 items (Q20), 1-5
  2. interpersonal_reactivity — Davis IRI, 15 items (Q15), 1-5
  3. intolerance_of_uncertainty — IU Scale, 16 items (Q16), 1-5
  4. social_intelligence — MSE Scale, 11 items (Q17), 1-5
  5. psychological_flexibility — PFQ, 9 items (Q18), 1-6
  6. grit — Short Grit Scale (SGS), 3 items (Q19), 1-5

Item labels use original scale item numbers from the codebook.

DOI: 10.7910/DVN/Y75CP2
License: CC0
"""

import os
import pandas as pd

QUEUE_FILE = "../automated_finding/irw_output/queue/10_7910_dvn_y75cp2.csv"
OUT_DIR    = "../automated_finding/irw_output/cleaned"
DOI        = "10.7910/DVN/Y75CP2"
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

# Maps from queue item name → original scale item name
SCALES = {
    "emotional_intelligence": {
        "Q20_1": "schutte_1",   "Q20_2": "schutte_2",   "Q20_3": "schutte_7",
        "Q20_4": "schutte_8",   "Q20_5": "schutte_9",   "Q20_6": "schutte_13",
        "Q20_7": "schutte_18",  "Q20_8": "schutte_19",  "Q20_9": "schutte_23",
        "Q20_10": "schutte_25", "Q20_11": "schutte_29", "Q20_12": "schutte_31",
        "Q20_13": "schutte_32", "Q20_14": "schutte_33",
    },
    "interpersonal_reactivity": {
        "Q15_1": "iri_1",  "Q15_2": "iri_3",  "Q15_3": "iri_5",
        "Q15_4": "iri_6",  "Q15_5": "iri_7",  "Q15_6": "iri_8",
        "Q15_7": "iri_12", "Q15_8": "iri_13", "Q15_9": "iri_15",
        "Q15_10": "iri_16", "Q15_11": "iri_21", "Q15_12": "iri_22",
        "Q15_13": "iri_23", "Q15_14": "iri_25", "Q15_15": "iri_26",
    },
    "intolerance_of_uncertainty": {
        "Q16_1": "iu_2",   "Q16_2": "iu_3",   "Q16_3": "iu_4",
        "Q16_4": "iu_5",   "Q16_5": "iu_8",   "Q16_6": "iu_10",
        "Q16_7": "iu_11",  "Q16_8": "iu_14",  "Q16_9": "iu_15",
        "Q16_10": "iu_16", "Q16_11": "iu_18", "Q16_12": "iu_21a",
        "Q16_13": "iu_21b", "Q16_14": "iu_23", "Q16_15": "iu_26",
        "Q16_16": "iu_27",
    },
    "social_intelligence": {
        "Q17_1": "mse_5",  "Q17_2": "mse_7",  "Q17_3": "mse_8",
        "Q17_4": "mse_9",  "Q17_5": "mse_10", "Q17_6": "mse_14",
        "Q17_7": "mse_16", "Q17_8": "mse_17", "Q17_9": "mse_18",
        "Q17_10": "mse_20", "Q17_11": "mse_21",
    },
    "psychological_flexibility": {
        "Q18_1": "pfq_1",  "Q18_2": "pfq_2",  "Q18_3": "pfq_4",
        "Q18_4": "pfq_5",  "Q18_5": "pfq_6",  "Q18_6": "pfq_9",
        "Q18_7": "pfq_13", "Q18_8": "pfq_16", "Q18_9": "pfq_18",
    },
    "grit": {
        "Q19_1": "grit_1", "Q19_2": "grit_3", "Q19_3": "grit_5",
    },
}

TITLES = {
    "emotional_intelligence":      "DPT Non-Cognitive Traits — Emotional Intelligence (Schutte)",
    "interpersonal_reactivity":    "DPT Non-Cognitive Traits — Interpersonal Reactivity (IRI)",
    "intolerance_of_uncertainty":  "DPT Non-Cognitive Traits — Intolerance of Uncertainty",
    "social_intelligence":         "DPT Non-Cognitive Traits — Social Intelligence (MSE)",
    "psychological_flexibility":   "DPT Non-Cognitive Traits — Psychological Flexibility (PFQ)",
    "grit":                        "DPT Non-Cognitive Traits — Grit (Short Grit Scale)",
}

RESP_RANGES = {
    "emotional_intelligence": "1-5",
    "interpersonal_reactivity": "1-5",
    "intolerance_of_uncertainty": "1-5",
    "social_intelligence": "1-5",
    "psychological_flexibility": "1-6",
    "grit": "1-5",
}

index_rows = []

for scale_name, item_map in SCALES.items():
    scale_df = df[df["item"].isin(item_map)].copy()
    scale_df["item"] = scale_df["item"].map(item_map)
    scale_df["resp"] = scale_df["resp"].astype(int)
    scale_df = scale_df.sort_values(["id", "item"]).reset_index(drop=True)

    out_file = f"dpt_noncog__{scale_name}.csv"
    scale_df.to_csv(os.path.join(OUT_DIR, out_file), index=False)

    n_p = scale_df["id"].nunique()
    n_i = scale_df["item"].nunique()
    n_r = len(scale_df)
    print(f"{scale_name}: {n_p} participants, {n_i} items, {n_r} rows")

    index_rows.append({
        "file": out_file, "doi": DOI,
        "title": TITLES[scale_name],
        "scale": scale_name,
        "n_participants": n_p, "n_items": n_i, "n_responses": n_r,
        "resp_range": RESP_RANGES[scale_name],
        "license": LICENSE,
        "notes": "item numbers match original scale numbering; item text in Dataverse Excel codebook",
        "status": "cleaned",
    })

update_index(OUT_DIR, index_rows)
print(f"\nSaved {len(index_rows)} scale files to {OUT_DIR}/")
