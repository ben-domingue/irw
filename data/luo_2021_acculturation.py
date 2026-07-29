#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260616
# DOI: 10.1371/journal.pone.0260616
# Supporting Information: https://doi.org/10.1371/journal.pone.0260616.s003
#
# Four instruments bundled in one file for international students in
# China: a 12-item attachment scale (ECR-style avoidance/anxiety items),
# a 12-item social-support-ties battery split across three friend groups
# (co-national, host, international -- 4 items each), a 10-item
# Acculturation Index, and a 2-item QCL block (excluded: fractional
# values with a min near 0.01 indicate an already-computed proportion,
# not a raw response). Item column headers in the source file are
# malformed by an Excel merge artifact -- only the first item in each
# block carries the real question text, and subsequent items are bare
# "@2."/"@3." placeholders -- so columns are selected by position, not by
# retyping the (occasionally non-ASCII) header text. "R"-suffixed
# duplicate columns (@6R, @8R, @9R, @10R, @11R, @12R) are the authors'
# own reverse-scored recodes of six ECR items and are dropped to avoid
# double-counting the same six responses; all *sum/average* columns are
# derived subscale scores and dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0260616.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_IDX = {1: "cov_gender", 2: "cov_age", 3: "cov_nationality",
           4: "cov_relationship_status", 5: "cov_religious_belief",
           6: "cov_duration_in_china", 7: "cov_chinese_proficiency",
           8: "cov_english_proficiency"}

ECR_IDX = [9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25]
CONATIONAL_IDX = list(range(31, 35))
HOST_IDX = list(range(35, 39))
INTL_IDX = list(range(39, 43))
ACCULT_IDX = list(range(49, 59))

EXPECTED_NCOLS = 65


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content), convert_categoricals=False)
    assert len(df.columns) == EXPECTED_NCOLS, \
        f"expected {EXPECTED_NCOLS} columns, got {len(df.columns)} -- source layout changed"

    cols = list(df.columns)
    df = df.rename(columns={cols[0]: "id", **{cols[i]: n for i, n in COV_IDX.items()}})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    cov_cols = list(COV_IDX.values())

    def item_names(idxs):
        return [cols[i] for i in idxs]

    scales = [
        ("luo_2021_ecr", item_names(ECR_IDX), 7),
        ("luo_2021_conational_ties", item_names(CONATIONAL_IDX), 4),
        ("luo_2021_host_ties", item_names(HOST_IDX), 5),
        ("luo_2021_intl_ties", item_names(INTL_IDX), 5),
        ("luo_2021_acculturation_index", item_names(ACCULT_IDX), 5),
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, item_cols, valid_max in scales:
        renamed = {c: f"item_{i+1:02d}" for i, c in enumerate(item_cols)}
        sub = df[["id"] + cov_cols + item_cols].rename(columns=renamed)
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=list(renamed.values()),
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= 1) & (long["resp"] <= valid_max)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]

        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
