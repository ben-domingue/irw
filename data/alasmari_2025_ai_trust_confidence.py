#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331003
# DOI: 10.1371/journal.pone.0331003
# SI: S1 Data (10.1371/journal.pone.0331003.s001), XLSX
#
# "Demographic influences on trust in artificial intelligence across
# cognitive domains: A statistical perspective". N=335, no explicit
# participant-id column in the raw file -> use row index as id.
#
# The raw file bundles two distinct constructs in one sheet:
#   (1) confidence in performing four cognitive tasks (this script) --
#       4-point ordinal: Not confident < Neutral < Somewhat confident <
#       Very confident.
#   (2) comparative AI-vs-human trust across five domains (separate
#       script: alasmari_2025_ai_trust_compare.py) -- different response
#       category set, so kept as its own file per datastandard.md
#       ("one scale per file").
#
# Paper's own Methods text confirms complete data ("All responses were
# complete, and no missing data were observed; therefore, no data
# imputation or exclusion was necessary.") -- no imputation to worry about.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0331003.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "  Age": "cov_age",
    " Gender": "cov_gender",
    " Familiarty": "cov_ai_familiarity",
    "Frequent use": "cov_ai_use_frequency",
}

ITEM_COLS = {
    "Simple decisions ": "item_simple_decisions",
    " Complex decision ": "item_complex_decisions",
    " Memory recall ": "item_memory_recall",
    " Solving mathematical ": "item_math_problem_solving",
}

RESP_MAP = {
    "not confident": 1,
    "neutral": 2,
    "somewhat confident": 3,
    "very confident": 4,
}


def _clean(s):
    return s.astype(str).str.strip("[] ").str.strip().str.lower()


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    df = df.rename(columns=COV_MAP)
    for c in COV_MAP.values():
        df[c] = _clean(df[c])

    df = df.rename(columns=ITEM_COLS)
    item_col_names = list(ITEM_COLS.values())
    for c in item_col_names:
        df[c] = _clean(df[c])

    cov_cols = list(COV_MAP.values())
    long = df[["id"] + cov_cols + item_col_names].melt(
        id_vars=["id"] + cov_cols, value_vars=item_col_names,
        var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(RESP_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "alasmari_2025_ai_trust_confidence.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
