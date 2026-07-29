#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0316703
# DOI: 10.1371/journal.pone.0316703
# Supporting Information: https://doi.org/10.1371/journal.pone.0316703.s002
#
# DASS-21 (21 items, 0-3 scale) administered identically to two
# independently-recruited samples (Wave 1 N=519, Wave 2 N=455) -- Methods
# text confirms identical wording/scale ("Items are scored on a 4-point
# scale from 0 ... to 3 ...") in both waves, so merged into one file per
# datastandard.md's "same instrument administered to multiple sub-studies"
# rule, with id offset by 100000*sample and a cov_sample indicator (not a
# `wave` column -- these are different people, not repeat measures).
#
# The "5Ts" TMD-symptom items are dropped: the paper describes them as a
# binary yes/no measure in both waves, but the raw Wave 2 columns contain
# values 0-3, contradicting that description -- too inconsistent with the
# source text to ship without a codebook confirming which is correct.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0316703.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DASS_ITEMS = [f"DASS_{i}" for i in range(1, 22)]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    xl = pd.ExcelFile(io.BytesIO(r.content))

    frames = []
    for sample, sheet in enumerate(["WAVE 1", "WAVE 2"], start=1):
        df = pd.read_excel(xl, sheet)
        df = df.rename(columns={"No": "id", "Age": "cov_age", "Gender": "cov_gender"})
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"]).reset_index(drop=True)
        assert df["id"].nunique() == len(df), f"id not unique in {sheet}"
        df["id"] = df["id"].astype(int) + 100000 * sample
        df["cov_sample"] = sample
        frames.append(df[["id", "cov_age", "cov_gender", "cov_sample"] + DASS_ITEMS])

    df = pd.concat(frames, ignore_index=True)
    assert df["id"].nunique() == len(df), "id not unique after combining samples"

    cov_cols = ["cov_age", "cov_gender", "cov_sample"]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=DASS_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 3)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "xiong_2025_dass21.csv"
    long.to_csv(out_path, index=False)
    print(f"xiong_2025_dass21: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
