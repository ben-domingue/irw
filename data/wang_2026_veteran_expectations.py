#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0351162
# DOI: 10.1371/journal.pone.0351162
# S1 File (raw survey data): https://doi.org/10.1371/journal.pone.0351162.s001
#   (resolves to https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0351162.s001&type=supplementary)
#
# Paper: Wang et al. (2026). "Research on incentive mechanisms for
# veterans' participation in grassroots governance: An analysis based on
# behavioral expectations." PLOS ONE.
#
# Only the Behavioral Expectations (BE) construct (B1-B3, a 7-point Likert
# scale measured with Cronbach's alpha) is shipped. The raw file's other
# columns (C11-C33, D1-D2) mix categorical exposure-frequency codes,
# 0-10 attractiveness ratings for different named incentive types, and
# already-banded behavioral-frequency/percentage indicators used as a
# formative composite (Composite Reliability, not a reflective Likert
# scale) for "Policy Instruments" / "Participation Behavior" per the
# paper's Methods -- there's no documented per-column item mapping in the
# supplementary file (unlike a codebook sheet), and mixing a categorical
# frequency code with a 0-10 rating in one construct doesn't fit IRW's
# single-instrument-per-file item-response format. B1-B3 alone is a clean,
# well-defined multi-item reflective scale and is shipped on its own.

import os
import pandas as pd
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0351162.s001&type=supplementary"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "A1": "cov_service_years",
    "A2": "cov_rank",
    "A3": "cov_monthly_income",
}
ITEM_COLS = ["B1", "B2", "B3"]


def fetch_raw():
    local = os.path.join(BASE, "pone0351162_s001.xlsx")
    if not os.path.exists(local):
        r = requests.get(URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(local, "wb") as f:
            f.write(r.content)
    return local


def convert():
    raw = fetch_raw()
    df = pd.read_excel(raw, sheet_name="Sheet1")
    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique"

    df = df.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    sub = df[["id"] + cov_cols + ITEM_COLS]
    long = sub.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                     var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # documented scale is 1-7
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)].reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]
    out_name = "wang_2026_veteran_expectations"
    path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(path, index=False)
    print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
