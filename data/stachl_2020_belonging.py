#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0233431
# DOI: 10.1371/journal.pone.0233431
# Stachl & Baranger (2020), "Sense of belonging within the graduate
# community of a research-focused STEM department: Quantitative assessment
# using a visual narrative and item response theory", PLOS ONE. CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0233431.s002

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0233431.s002"


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    # Row 0 is a banner label, row 1 is a repeat header ("Respondent",
    # "Better Grades", ...) -- the true column names.
    df = pd.read_excel(io.BytesIO(r.content), header=2)
    df = df.rename(columns={"Respondent": "id"})
    item_cols = [c for c in df.columns if c != "id"]

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    # "." is the sentinel for a skipped item.
    long["resp"] = long["resp"].replace(".", pd.NA)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    path = os.path.join(OUT_DIR, "stachl_2020_belonging.csv")
    long.to_csv(path, index=False)
    print(f"stachl_2020_belonging: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
