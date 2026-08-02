#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249815
# DOI: 10.1371/journal.pone.0249815
# Daiku, Serota & Levine (2021), "A few prolific liars in Japan: Replication
# and the effects of Dark Triad personality traits", PLOS ONE. CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0249815.s001

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "irw-batch/1.0 (research)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0249815.s001"

SCALES = {
    "daiku_2021_dirty_dozen": [
        "machiavellianism1", "machiavellianism2", "machiavellianism3", "machiavellianism4",
        "psychopathy1", "psychopathy2", "psychopathy3", "psychopathy4",
        "narcissism1", "narcissism2", "narcissism3", "narcissism4",
    ],
    "daiku_2021_lie_scale": ["liescale1", "liescale2", "liescale3"],
    "daiku_2021_lying_frequency": [
        "family_direct", "family_indirect", "friend_direct", "friend_indirect",
        "business_direct", "business_indirect", "clerk_direct", "clerk_indirect",
        "stranger_direct", "stranger_indirect",
    ],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", "sex": "cov_sex", "age": "cov_age"})
    return df


def convert():
    df = fetch()
    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id", "cov_sex", "cov_age"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "cov_sex", "cov_age"]]
        path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
