#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0138153
# DOI: 10.1371/journal.pone.0138153
# Supporting Information: https://doi.org/10.1371/journal.pone.0138153.s001
#
# The raw file is transposed relative to the usual layout: rows are face
# stimuli (F01-F24), columns are subjects (S01-S16), and cell values are
# each subject's facial-preference-value (FPV) for that face -- the
# proportion of times, across repeated presentations, the subject rated
# that face as preferred (continuous, 0-1). The trailing "mean FPV" column
# is a per-face average across subjects (an aggregate), not a subject, and
# is dropped. Reshaped here so id=subject, item=face, resp=FPV.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0138153.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"Unnamed: 0": "item"})
    df = df.drop(columns=["mean FPV"])

    subject_cols = [c for c in df.columns if c != "item"]
    long = df.melt(id_vars=["item"], value_vars=subject_cols,
                    var_name="id", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "kang_2015_facial_preference.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.2f}-{long['resp'].max():.2f}")


if __name__ == "__main__":
    convert()
