#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0304428
# DOI: 10.1371/journal.pone.0304428
# Supporting Information: https://doi.org/10.1371/journal.pone.0304428.s002
#
# Qualtrics export with 2 extra header rows (question text, ImportId JSON)
# above the data -- skiprows=[1,2]. Item text (row 1) confirms 4 usable
# raw-item blocks: Q20 (16 items, personality/"characteristics that may or
# may not apply to you", BFI-style), Q21 (4 items, PSS-4 wording), Q22 (4
# items, PHQ-4 wording), Q26 (6 binary items, subjective cognitive
# decline). Q23-Q25 (loneliness/social-network contact-frequency items)
# were judged lower-value/more demographic-flavored and skipped to manage
# scope. SC1-12 are separately-computed instrument TOTALS (row-1 label is
# literally the instrument name, e.g. SC1="PSS", value range 0-16 matching
# a PSS-4 sum) -- aggregates, excluded, not raw items.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0304428.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_Q20 = {"Disagree strongly": 1, "Disagree a little": 2, "Neutral: no opinion": 3,
           "Agree a little": 4, "Agree strongly": 5}
MAP_Q21 = {"Never": 0, "Almost never": 1, "Sometimes": 2, "Fairly often": 3, "Very often": 4}
MAP_Q22 = {"Not at all": 0, "Several days": 1, "More than half the days": 2, "Nearly every day": 3}
MAP_Q26 = {"No": 0, "Yes": 1}

SCALES = {
    "cormier_2024_personality": ([f"Q20_{i}" for i in range(1, 17)], MAP_Q20),
    "cormier_2024_pss4": ([f"Q21_{i}" for i in range(1, 5)], MAP_Q21),
    "cormier_2024_phq4": ([f"Q22_{i}" for i in range(1, 5)], MAP_Q22),
    "cormier_2024_cognitive_decline": ([f"Q26_{i}" for i in range(1, 7)], MAP_Q26),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), header=0, skiprows=[1, 2])
    return df.rename(columns={"ResponseId": "id"})


def melt_scale(df: pd.DataFrame, item_cols: list[str], value_map: dict, out_name: str):
    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    for out_name, (item_cols, value_map) in SCALES.items():
        melt_scale(df, item_cols, value_map, out_name)


if __name__ == "__main__":
    convert()
