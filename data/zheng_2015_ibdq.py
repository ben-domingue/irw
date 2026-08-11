#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0124211
# DOI: 10.1371/journal.pone.0124211
# SI: S1 Dataset ("Research data"), XLS
#
# Health-Related Quality of Life in Chinese Patients with Mild and
# Moderately Active Ulcerative Colitis. Instrument is the Chinese
# version of the Inflammatory Bowel Disease Questionnaire (IBDQ): 32
# items ("Question1"..."Question32" in the source, in Chinese) across
# 4 domains (bowel symptoms, systemic symptoms, emotional function,
# social function), each scored on a 7-point Likert scale (1-7, higher
# = better function). The source person-identifier column is a
# name-initials string that is NOT unique (220 unique values across
# 224 rows) -- row index is used as `id` instead per datastandard.md's
# "Missing person ID" guidance (a non-unique candidate id is treated
# the same as a missing one).

import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "journal.pone.0124211_S1_Dataset.xls")
SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0124211.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")

OUT_NAME = "zheng_2015_ibdq"


def convert():
    if not os.path.exists(RAW):
        import requests
        r = requests.get(SI_URL, headers=UA, timeout=60)
        r.raise_for_status()
        with open(RAW, "wb") as f:
            f.write(r.content)

    df = pd.read_excel(RAW, sheet_name=0)
    item_cols = [c for c in df.columns if str(c).startswith("问题")]
    assert len(item_cols) == 32, f"expected 32 IBDQ items, got {len(item_cols)}"

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    # item labels: use "ibdq_1".."ibdq_32" instead of Chinese question text
    item_map = {c: f"ibdq_{i}" for i, c in enumerate(item_cols, 1)}
    long["item"] = long["item"].map(item_map)

    long = long[["id", "item", "resp"]]
    path = os.path.join(OUT_DIR, f"{OUT_NAME}.csv")
    long.to_csv(path, index=False)
    print(f"{OUT_NAME}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
