from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0323879
# DOI: 10.1371/journal.pone.0323879
# Ngo & Nguyen (2025), "Exploring green purchasing intentions and
# behaviours among Vietnamese Generation Z: A perspective from the theory
# of planned behaviour". S1 File. CC BY 4.0. N=237.
# Standard Theory-of-Planned-Behaviour battery, 5 constructs x 4 items
# each, 1-5 Likert: Attitude (ATT), Subjective Norm (SN), Perceived
# Behavioral Control (PBC), Purchase Intention (PI), Purchase Behavior
# (PB) -- shipped as 5 separate scale files per datastandard.md's
# one-scale-per-file rule.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0323879.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Gender": "cov_gender", "Age": "cov_age", "Education": "cov_education",
           "Martial_status": "cov_marital_status", "E_L": "cov_english_level"}

SCALES = {
    "ngo_2025_green_attitude": ["G_ATT_1", "G_ATT_2", "G_ATT_3", "G_ATT_4"],
    "ngo_2025_green_subjective_norm": ["G_SN_1", "G_SN_2", "G_SN_3", "G_SN_4"],
    "ngo_2025_green_pbc": ["G_PBC_1", "G_PBC_2", "G_PBC_3", "G_PBC_4"],
    "ngo_2025_green_purchase_intention": ["G_PI_1", "G_PI_2", "G_PI_3", "G_PI_4"],
    "ngo_2025_green_purchase_behavior": ["G_PB_1", "G_PB_2", "G_PB_3", "G_PB_4"],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns=COV_MAP)
    df["id"] = df["No"]
    return df


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
