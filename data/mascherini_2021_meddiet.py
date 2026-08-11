#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0252395
# DOI: 10.1371/journal.pone.0252395
# Supporting Information: https://doi.org/10.1371/journal.pone.0252395.s001
#
# S1 File "Results of questionnaire" (XLSX), two sheets: "pre covid" (wave 1)
# and "during quarantine" (wave 2), row-matched (verified age/etc identical
# across corresponding rows in both sheets).
#
# Only the Med Diet Score food-frequency items are raw item-level data
# (each of 11 food groups rated 0-5 individually before being summed into
# the "Mediterranean SCORE D" composite). The wellbeing questionnaire
# columns (TENSE/DEPRESSION/CHEERFUL/FIRM CONTROL/CARRY OUT/ENERGY) are
# described in the paper as the six *subscale* scores of the 22-item
# PGWBI-A, not raw items - composite, excluded. METs/Sedentary columns are
# a different construct (activity, not diet) and are themselves derived
# summaries - excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0252395.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["Grains", "Potatoes", "Fruits", "Vegetables", "Legumes",
             "Fish", "Red meat", "White meat", "Dairy ", "Oil", "Alchool"]

COV_RENAME = {
    "Age - years": "cov_age",
    "Gender": "cov_gender",
    "Marital status": "cov_marital_status",
    "Education": "cov_education",
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    content = io.BytesIO(r.content)

    frames = []
    for wave, sheet in [(1, "pre covid"), (2, "during quarantine")]:
        d = pd.read_excel(content, sheet_name=sheet)
        d = d.reset_index(drop=True)
        d.insert(0, "id", d.index + 1)
        d["wave"] = wave
        d = d.rename(columns=COV_RENAME)
        cov_cols = list(COV_RENAME.values())
        keep = ["id", "wave"] + cov_cols + ITEM_COLS
        frames.append(d[keep])

    df = pd.concat(frames, ignore_index=True)

    long = df.melt(
        id_vars=["id", "wave"] + list(COV_RENAME.values()),
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["item"] = long["item"].str.strip().str.lower().str.replace(" ", "_")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 5)]

    out_cols = ["id", "item", "resp", "wave"] + list(COV_RENAME.values())
    long = long[out_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "mascherini_2021_meddiet.csv"
    long.to_csv(out_path, index=False)
    print(f"mascherini_2021_meddiet: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
