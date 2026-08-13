#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0261717
# DOI: 10.1371/journal.pone.0261717
#
# Srivani, Hariharasudan, Nawaz & Ratajczak (2022), "Impact of Education 4.0
# among engineering students for learning English language." PLOS ONE.
# CC BY 4.0. N=145 engineering students.
#
# Raw data: S2 File (https://doi.org/10.1371/journal.pone.0261717.s003), an
# XLSX with three sheets. "Data Statement Sheet" holds the raw per-respondent
# item responses (145 rows x 11 items, Q1-Q11, one row per student, no id
# column in the source -- row order used as id). Items are abbreviated
# (EEL, ELL, EDF, ELE, ECE, ELN, ELC, LET, ELS, TDE, ECT); the "Codings of
# Questionnaire" sheet maps each abbreviation to its full statement text
# (a 3-point-ish agreement scale on Education 4.0's impact on English
# language learning). The "Cummulative Summary" sheet is a derived
# aggregate (means/totals) and is not used here.
#
# resp values are 0/1/2 for nearly all responses, with a small number of -1
# values scattered across 5 of the 11 items (20 of 1595 cell values, ~1.3%).
# -1 doesn't appear at all in the other 6 items and the paper's own
# 3-point scale description has no negative code, so these are treated as
# data-entry errors / sentinel values and dropped (rows-per-item, not
# whole respondents).
#
# No PII in the source file -- no names, emails, or free text, only coded
# integer responses.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.1371/journal.pone.0261717"
SI_URL = (
    "https://journals.plos.org/plosone/article/file"
    "?id=10.1371/journal.pone.0261717.s003&type=supplementary"
)
UA = {"User-Agent": "irw-batch/1.0 (research)"}

OUT_NAME = "srivani_2022_education4.csv"


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Data Statement Sheet")
    # First row of the sheet duplicates the header labels; the real header
    # (Q1..Q11) is already picked up by pandas as the column names.
    df = df.iloc[1:].reset_index(drop=True)
    return df


def convert():
    print("Downloading S2 File …")
    raw = fetch_data()

    item_map = {
        "Q1": "EEL", "Q2": "ELL", "Q3": "EDF", "Q4": "ELE", "Q5": "ECE",
        "Q6": "ELN", "Q7": "ELC", "Q8": "LET", "Q9": "ELS", "Q10": "TDE",
        "Q11": "ECT",
    }
    raw = raw.rename(columns=item_map)
    item_cols = list(item_map.values())

    raw.insert(0, "id", raw.index + 1)

    long = raw.melt(
        id_vars=["id"],
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    # Drop the sparse -1 sentinel/data-entry-error values (see header note)
    long = long[long["resp"].isin([0, 1, 2])].reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / OUT_NAME
    long.to_csv(out_csv, index=False)
    print(
        f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}"
    )


if __name__ == "__main__":
    convert()
