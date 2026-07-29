#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256636
# DOI: 10.1371/journal.pone.0256636
# Supporting Information: https://doi.org/10.1371/journal.pone.0256636.s001
#
# RPAP (Risk Perception, Attitude, Practice) dengue questionnaire, main
# validation sample (Sheet1, N=253; Sheet3 is a separate N=67 test-retest
# subsample and not processed here). Raw items are split into three
# domain blocks per Table 2 of the paper -- D (risk perception, 12 items),
# E (attitude, 10 items), F (practice, 13 items) -- all on the same 8-point
# Likert scale. Ships all raw items as collected; the paper's own 29-item
# "final version" is a post-hoc reduced subset for scoring purposes, not a
# raw-response distinction.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0256636.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = [
    ("zamzuri_2021_rpap_risk_perception", "D"),
    ("zamzuri_2021_rpap_attitude", "E"),
    ("zamzuri_2021_rpap_practice", "F"),
]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")
    df = df.rename(columns={"Bil": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, prefix in SCALES:
        item_cols = [c for c in df.columns if c.startswith(prefix) and c[len(prefix):].isdigit()]

        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= 1) & (long["resp"] <= 8)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
