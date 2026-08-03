#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0236098
# DOI: 10.1371/journal.pone.0236098
# Hicks et al. (2020), "Development of the Biological Variation In
# Experimental Design And Analysis (BioVEDA) assessment", PLOS ONE. CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0236098.s003

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0236098.s003"

ITEM_COLS = [f"Q{i}" for i in range(1, 17)]


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"Study_ID": "id", "Role": "cov_role"})

    long = df.melt(id_vars=["id", "cov_role"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "cov_role"]]

    path = os.path.join(OUT_DIR, "hicks_2020_bioveda.csv")
    long.to_csv(path, index=False)
    print(f"hicks_2020_bioveda: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
