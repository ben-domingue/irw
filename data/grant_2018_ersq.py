#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0205095
# DOI: 10.1371/journal.pone.0205095
# Supporting Information: https://doi.org/10.1371/journal.pone.0205095.s001
#
# The Emotion Regulation Skills Questionnaire (27 items) was administered
# pre- and post-intervention (preers1-27, posers1-27) -- a genuine 2-wave
# design, encoded here as wave=1 (pre) / wave=2 (post). The predx*/precsr*/
# posdx*/poscsr* columns (a separate diagnostic-checklist instrument) and
# all *total/*clin/*coprindx columns (derived composites) are not part of
# this scale and are excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0205095.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {"Not at all": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Almost always": 4}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"UPID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    pre_cols = [f"preers{i}" for i in range(1, 28)]
    post_cols = [f"posers{i}" for i in range(1, 28)]
    for c in pre_cols + post_cols:
        df[c] = df[c].astype(str).map(LIKERT_MAP)

    pre = df.melt(id_vars=["id"], value_vars=pre_cols, var_name="item", value_name="resp")
    pre["item"] = pre["item"].str.replace("preers", "ers", regex=False)
    pre["wave"] = 1

    post = df.melt(id_vars=["id"], value_vars=post_cols, var_name="item", value_name="resp")
    post["item"] = post["item"].str.replace("posers", "ers", regex=False)
    post["wave"] = 2

    long = pd.concat([pre, post], ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "grant_2018_ersq.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
