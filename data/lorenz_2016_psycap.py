#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0152892
# DOI: 10.1371/journal.pone.0152892
# Supporting Information (Study 1): https://doi.org/10.1371/journal.pone.0152892.s002
#
# Study 1 raw data for the Compound PsyCap Scale (CPC-12) validation. The
# file is semicolon-delimited (triage originally read it with comma
# delimiter, which merged every column into one). Bundles six distinct
# item batteries -- hope, two optimism batteries, resilience (CD-RISC-13),
# two self-efficacy batteries, and the 24-item PsyCap item pool the CPC-12
# was drawn from -- each written as its own file per datastandard.md's
# one-scale-per-file rule. No person ID or covariate columns exist in the
# source file; row index is used as id.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0152892.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "lorenz_2016_hope": [f"hope{i}" for i in range(1, 7)],
    "lorenz_2016_optimism1": [f"optimism1.{i}" for i in range(1, 6)],
    "lorenz_2016_optimism2": [f"optimism2.{i}" for i in range(1, 11)],
    "lorenz_2016_resilience": [f"resilience{i}" for i in range(1, 14)],
    "lorenz_2016_efficacy1": [f"efficacy1.{i}" for i in range(1, 11)],
    "lorenz_2016_efficacy2": [f"efficacy2.{i}" for i in range(1, 9)],
    "lorenz_2016_psycap": [f"psycap{i}" for i in range(1, 25)],
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), sep=";")
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
