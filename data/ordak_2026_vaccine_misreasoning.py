#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0355341
# DOI: 10.1371/journal.pone.0355341
# Supporting Information: https://doi.org/10.1371/journal.pone.0355341.s001
#
# 597 Polish-language anti-vaccination Facebook posts, each hand-coded by
# the study team for the presence (1) or absence (0) of 10 distinct types
# of statistical misreasoning (correlation-causation fallacy, base rate
# neglect, denominator neglect, cherry picking, relative-vs-absolute risk
# error, small sample fallacy, intuitive reasoning error, random
# fluctuation misinterpretation, overinterpretation of percentages,
# graphical scale misreading). No validated survey instrument was
# administered to human respondents -- the focal unit here is the post
# (`id`), and each of the 10 coding categories is an `item` with a binary
# `resp`. This fits IRW's checklist/binary-item-response shape (analogous
# to a symptom checklist), consistent with prior non-human-respondent
# tables shipped in this pipeline (e.g. dog-cognition data).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0355341.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

OUT_NAME = "ordak_2026_vaccine_misreasoning"

ITEM_RENAME = {
    "Correlation–causation fallacy": "correlation_causation",
    "Base rate neglect": "base_rate_neglect",
    "Denominator neglect": "denominator_neglect",
    "Cherry picking": "cherry_picking",
    "Relative vs absolute risk error": "relative_absolute_risk",
    "Small sample fallacy": "small_sample_fallacy",
    "Intuitive reasoning error": "intuitive_reasoning",
    "Random fluctuation misinterpretation": "random_fluctuation",
    "Overinterpretation of percentages": "overinterpretation_pct",
    "Graphical scale misreading": "graphical_scale_misreading",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"Post_ID": "id"})
    df = df.rename(columns=ITEM_RENAME)

    assert df["id"].nunique() == len(df), "id column is not unique per post"

    item_cols = list(ITEM_RENAME.values())

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{OUT_NAME}.csv"
    long.to_csv(out_path, index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
