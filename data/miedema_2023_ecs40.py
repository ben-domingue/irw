#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0287963
# DOI: 10.1371/journal.pone.0287963
#
# "Development and validation of the Economic Coercion Scale-20 (ECS-20):
# A short-form of the ECS-36" (Miedema et al., 2023)
#
# S1 Dataset (DTA), N=930 (Bangladesh field survey). Raw item-level binary
# Yes/No responses to the full ~40-item Economic Coercion Scale item pool
# (`ecoscale_<n>`), used in the paper to derive the ECS-36/ECS-20
# short-forms via factor analysis. Each base item has associated `_a`/`_b`
# follow-up sub-questions (perpetrator identity, frequency) that are
# conditional, different-content, different-response-scale items, not part
# of the core Yes/No coercion-experience battery -- excluded here.
# Response text is bilingual (English/Bangla); recoded Yes=1, No=0.
# "DO NOT READ: Refused" and blank/NaN are dropped as non-responses, not
# valid scale points. No demographic/covariate columns are present in the
# raw file (record_id + item columns only).

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://doi.org/10.1371/journal.pone.0287963.s001"

RESP_MAP = {
    "Yes": 1,
    "No": 0,
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(DATA_URL, headers=UA, timeout=60)
    r.raise_for_status()
    from io import BytesIO
    return pd.read_stata(BytesIO(r.content))


def recode(val):
    if not isinstance(val, str):
        return None
    if val.startswith("Yes"):
        return 1
    if val.startswith("No") and not val.startswith("DO NOT"):
        return 0
    return None  # "DO NOT READ: Refused" or other non-response


def convert():
    print("Downloading S1 Dataset …")
    df = fetch_data()
    df = df.rename(columns={"record_id": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id not unique"

    item_cols = [c for c in df.columns if re.match(r"^ecoscale_\d+$", c)]

    long = df[["id"] + item_cols].melt(
        id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp_raw"
    )
    long["resp"] = long["resp_raw"].apply(recode)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "miedema_2023_ecs40.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
