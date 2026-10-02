#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/R6WE4P
# DOI: 10.7910/DVN/R6WE4P
# License: CC0 1.0
#
# "Replication Data for: Streamlining measurements of gendered personality:
# integrating the Bem Sex-role inventory into national surveys" (Holden,
# 2026, Harvard Dataverse). The raw file (GPAPMS Final Data.tab) had
# automatically landed in the `aggregate_continuous` retriage bucket
# (dup_id_item ratio 11x on a mis-detected id column) -- manually confirmed
# instead: the 20 raw BSRI trait-rating items are self-descriptively named
# ("Willing to take risks", "Forceful", "Warm", ... -- the standard 20-item
# BSRI short form, 10 masculine + 10 feminine traits), each a clean 1-7
# self-rating Likert item, no missingness. No id column in the source file
# -- used row index as id (N=695, one row per respondent). Other columns
# (Cluster_*, BSRI_M/F, Gender6, Party_3/7, Q7/Q8a-c, News_Attention, etc.)
# are derived cluster/composite scores or unrelated political-survey items
# -- out of scope for this table.
#
# Item codes are neutral (irw#2101). The BSRI is copyrighted (Mind Garden; rights
# register row MIND-GARDEN = block), and the source columns are the trait adjectives
# themselves, so using them as codes published the instrument in the response table.
# BSRI_M01..M10 are the 10 masculine traits and BSRI_F01..F10 the 10 feminine ones,
# each numbered in the deposit's column order (CODES below). The split reproduces the
# deposit's own BSRI_M / BSRI_F composites exactly (item mean, r = 1.0, checked
# 2026-09-30). The 1-7 ratings are all keyed the same way; nothing needs reversing.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

FILE_URL = "https://dataverse.harvard.edu/api/access/datafile/14082100"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = [
    "Willing to take risks", "Understanding", "Forceful", "Strong personality",
    "Sympathetic", "Warm", "Assertive", "Loves children", "Independent",
    "Compassionate", "Gentle", "Leadership ability", "Aggressive",
    "Eager to soothe hurt feelings", "Affectionate", "Dominant",
    "Willing to take a stand", "Sensitive to needs of others",
    "Defends own beliefs", "Tender",
]
MASCULINE = {"Willing to take risks", "Forceful", "Strong personality", "Assertive",
             "Independent", "Leadership ability", "Aggressive", "Dominant",
             "Willing to take a stand", "Defends own beliefs"}
CODES, _n = {}, {"M": 0, "F": 0}
for _col in ITEMS:
    _k = "M" if _col in MASCULINE else "F"
    _n[_k] += 1
    CODES[_col] = f"BSRI_{_k}{_n[_k]:02d}"
assert _n == {"M": 10, "F": 10}
COV_MAP = {"CRC_Age": "cov_age", "CRC_Sex": "cov_sex", "CRC_Gender": "cov_gender",
           "CRC_Race": "cov_race", "CRC_Education": "cov_education"}


def convert():
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.BytesIO(r.content), sep="\t")
    df = df.rename(columns=COV_MAP)
    df.insert(0, "id", range(1, len(df) + 1))
    cov_cols = list(COV_MAP.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long["item"] = long["item"].map(CODES)
    assert long["item"].notna().all()
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "holden_2026_bsri"
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
