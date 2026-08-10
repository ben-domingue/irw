#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0261652
# DOI: 10.1371/journal.pone.0261652
#
# Forycka et al. (2022) "Polish medical students facing the pandemic --
# Assessment of resilience, well-being and burnout in the COVID-19 era."
# PLOS ONE. License: CC BY 4.0.
#
# S2 File (XLSX, N=1858) has raw item-level responses for three licensed
# psychometric instruments. Per the paper's Data Availability statement,
# the AUTHORS blinded the column HEADINGS (generic MBI#/WBI#/RS# labels
# instead of the literal copyrighted question wording) because they cannot
# publicly share the licensed instruments' question text -- but the numeric
# response matrix itself is shared under CC BY 4.0 and is exactly what IRW
# needs (item text is not required; see datastandard.md "No meaningful item
# labels"). One file per scale (datastandard.md "one scale per file"):
#   - Maslach Burnout Inventory-General Survey for Students (MBI-GS(S)):
#     MBI1-16 (16 items, 0-6 scale)
#   - Medical Students' Well-Being Index (MSWBI): WBI1-7 (7 items, 0-1 scale)
#   - Resilience Scale-14 (RS-14): RS1-14 (14 items, 1-7 scale)

import os

import pandas as pd
import requests
import io

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0261652.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Year of medical school": "cov_school_year",
}

SCALES = {
    "forycka_2022_mbi_gss": ([f"MBI{i}" for i in range(1, 17)], 0, 6),
    "forycka_2022_mswbi": ([f"WBI{i}" for i in range(1, 8)], 0, 1),
    "forycka_2022_rs14": ([f"RS{i}" for i in range(1, 15)], 1, 7),
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    print("Fetching S2 File (XLSX)...")
    raw = fetch_raw()
    df = raw.rename(columns=COV_RENAME)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].is_unique

    # WBI items are Polish Yes/No strings ("Tak"/"Nie"), not numeric --
    # map to 1/0 before the generic numeric-scale melt below.
    for c in [f"WBI{i}" for i in range(1, 8)]:
        df[c] = df[c].map({"Tak": 1, "Nie": 0})

    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, (item_cols, lo, hi) in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        for c in item_cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
