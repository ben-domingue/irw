#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0174947
# DOI: 10.1371/journal.pone.0174947
# Supporting Information: https://doi.org/10.1371/journal.pone.0174947.s002
#
# Raw file has a 26-item, 1-7 Likert questionnaire about lecture-hall
# seating motivations, plus a separate 7-item multi-select checklist of
# reasons for seat choice (marked 'O' / blank -> 1/0). Two output files.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0174947.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "IFSI": "cov_program",
    "SCHOOL": "cov_school_site",
    "YEAR": "cov_year",
    "RANK": "cov_seat_rank_preference",
}

QUESTION_COLS = [f"QUESTION{i}" if i < 10 else f"QUESTIO{i}" for i in range(1, 27)]
CHECKLIST_COLS = ["affinity", "habit", "noise", "practical", "remain",
                   "concentrate", "else"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"NB": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=QUESTION_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(OUT_DIR / "uffler_2017_lecture_seating.csv", index=False)
    print(f"uffler_2017_lecture_seating.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

    for c in CHECKLIST_COLS:
        df[c] = (df[c] == "O").astype(int)
    long2 = df.melt(id_vars=["id"] + cov_cols, value_vars=CHECKLIST_COLS,
                     var_name="item", value_name="resp")
    long2 = long2[["id", "item", "resp"] + cov_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long2.to_csv(OUT_DIR / "uffler_2017_seat_reasons.csv", index=False)
    print(f"uffler_2017_seat_reasons.csv: ids={long2['id'].nunique()} "
          f"items={long2['item'].nunique()} resp={long2['resp'].min()}-{long2['resp'].max()}")


if __name__ == "__main__":
    convert()
