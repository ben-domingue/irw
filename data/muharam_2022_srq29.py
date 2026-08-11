#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0270658
# DOI: 10.1371/journal.pone.0270658
# Supporting Information: https://doi.org/10.1371/journal.pone.0270658.s002
#
# Self Reporting Questionnaire-29 (SRQ-29): 29 binary (1=yes, 0=no)
# neurotic/psychoactive-substance/psychotic/PTSD screening items
# administered to women hospitalized for COVID-19. "Name (Initial)" and
# "Phone Number" columns are PII and are dropped; there is no other
# person-identifier column so row index is used as id.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0270658.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_PATTERN = re.compile(r"^SRQ-\d+ \(1=yes, 0=no\)$")


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.drop(columns=["Name (Initial)", "Phone Number"])  # PII
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def convert():
    df = fetch_data()
    item_cols = [c for c in df.columns if ITEM_PATTERN.match(str(c))]

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.extract(r"^(SRQ-\d+)")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "muharam_2022_srq29.csv", index=False)
    print(f"muharam_2022_srq29.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
