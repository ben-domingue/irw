from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0236987
# DOI: 10.1371/journal.pone.0236987
# Zhang et al. (2020), "Individual differences in trait creativity
# moderate the state-level mood-creativity relationship". S1 File. CC BY
# 4.0. N=54, experience-sampling design (multiple observations per
# person per day, `day` kept as wave). 12 raw 0-100 rating items:
# originality/usefulness (creative-task ratings) and 10 mood adjectives
# (relaxed/tired/happy/stressed/concentrated/active/angry/depressed/
# interested, plus a second "tired" column -- confirmed NOT a duplicate,
# only 5% value agreement with the first, so both kept as distinct items
# `tired`/`tired.1`). `valence`/`activation`/`regulatory focus` (likely
# derived composites) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0236987.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["originality", "usefulness", "relaxed", "tired", "happy", "stressed",
             "concentrated", "tired.1", "active", "angry", "depressed", "interested"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={"name": "id", "day": "wave"})


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id", "wave"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]
    out_path = OUT_DIR / "zhang_2020_trait_creativity_mood.csv"
    long.to_csv(out_path, index=False)
    print(f"zhang_2020_trait_creativity_mood: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
