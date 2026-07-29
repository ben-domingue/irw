#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0330447
# DOI: 10.1371/journal.pone.0330447
# Supporting Information: data collection spreadsheet, https://doi.org/10.6084/m9.figshare.29504990
#
# Chinese-language survey of N=345 college students with three scales in
# one file: Meaning in Life Questionnaire (9 items, 1-7), a Positive
# Cognition scale (12 items, 1-5), and a Learning Motivation scale
# (16 items, 1-5). Column names are the original Chinese question text;
# per datastandard.md's "Non-Latin item text in column names" edge case,
# items are relabeled item_1.. and the original Chinese text is kept in
# an item_text column for later matching. "来自IP" (source IP address) is
# PII and dropped entirely, not carried as a covariate.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0330447.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "3、您的性别：（男=1，女=0）": "cov_gender",
    "4、您的年龄是？": "cov_age",
    "5、您的家庭所在地？（城市=1，农村=0）": "cov_urban",
    "6、请问您是否是独生子女？（是=1，否=0）": "cov_only_child",
}

SCALES = [
    ("liu_2025_mlq", range(7, 16), 1, 7),
    ("liu_2025_positive_cognition", range(32, 44), 1, 5),
    ("liu_2025_learning_motivation", range(16, 32), 1, 5),
]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"序号": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    qmap = {}
    for c in df.columns:
        m = re.match(r"^(\d+)、", c)
        if m:
            qmap[int(m.group(1))] = c

    cov_cols = list(COV_RENAME.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, qrange, lo, hi in SCALES:
        src_cols = [qmap[i] for i in qrange]
        item_labels = {c: f"item_{i}" for i, c in enumerate(src_cols, start=1)}

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=src_cols,
                        var_name="item", value_name="resp")
        long["item_text"] = long["item"]
        long["item"] = long["item"].map(item_labels)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "item_text"] + cov_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
