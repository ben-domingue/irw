#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0229926
# DOI: 10.1371/journal.pone.0229926
# Supporting Information: https://doi.org/10.1371/journal.pone.0229926.s002
#
# 32-item Moral Foundations Questionnaire (MFQ-32), 0-5 scale, rated twice
# per respondent: once as the respondent's own moral judgment (bare item
# names) and once as their prediction of the "average person's" rating
# (STP_-prefixed items on the same 32 statements) -- written as two
# separate files since they're two distinct measurement conditions on the
# same items. MFQ_*_AVG / STP_*_AVG (foundation-level averages) are
# derived composites and dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0229926.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MFQ_ITEMS = ["EMOTIONALLY", "TREATED", "LOVECOUNTRY", "RESPECT", "DECENCY", "MATH",
             "WEAK", "UNFAIRLY", "BETRAY", "TRADITIONS", "DISGUSTING", "CRUEL",
             "RIGHTS", "LOYALTY", "CHAOS", "GOD", "COMPASSION", "FAIRLY", "HISTORY",
             "KIDRESPECT", "HARMLESSDG", "GOOD", "ANIMAL", "JUSTICE", "FAMILY",
             "SEXROLES", "UNNATURAL", "KILL", "RICH", "TEAM", "SOLDIER", "CHASTITY"]

COV_RENAME = {"age": "cov_age", "gender": "cov_gender", "EDUCATION": "cov_education"}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content), convert_categoricals=False)
    df = df.rename(columns={"subject": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    cov_cols = list(COV_RENAME.values())

    for prefix, out_name in [("", "niazi_2020_mfq"), ("STP_", "niazi_2020_mfq_stereotype")]:
        item_cols = [f"{prefix}{c}" for c in MFQ_ITEMS]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= 0) & (long["resp"] <= 5)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
