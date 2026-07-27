#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0266507
# DOI: 10.1371/journal.pone.0266507
# Supporting Information: https://doi.org/10.1371/journal.pone.0266507.s001
#
# Two studies pooled; `id` is only unique WITHIN a study (per the file's
# own "Keys" sheet: "Participant's ID within the study") -- composite
# study-id used. Raw file has 3 scales: Eating Disorder Examination
# Questionnaire (EDE-Q, 28 items), Body Shape Questionnaire (BSQ, 16
# items), Rosenberg Self-Esteem Scale (RSES, 10 items) -- all confirmed
# via the Keys codebook sheet, not guessed. Two different missing-value
# sentinels are used within EDE-Q depending on item type (confirmed
# empirically: items 13-18 are frequency COUNTS, sentinel 99; all other
# EDE-Q items are 0-6 severity ratings, sentinel 9). BSQ/RSES use sentinel
# 8 ("not included in this study" -- some items were only administered in
# one of the two studies) and 9 (missing) -- both filtered. RSES here is
# coded 1=completely agree .. 4=completely disagree (not recoded, per the
# standard's "don't recode reverse-scored items" rule). All *_overall/
# subscale-total columns (edeq14_overall, edeq_dr/ec/ac/swoe, bsq8_overall,
# rses_nse/pse) are aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0266507.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"sex": "cov_sex", "age": "cov_age", "education": "cov_education"}

EDEQ_TIMES_ITEMS = {13, 14, 15, 16, 17, 18}   # frequency-count items, sentinel 99
EDEQ_COLS = [f"edeq_i{i:02d}" for i in range(1, 29)]
BSQ_COLS = [f"bsq_i{i:02d}" for i in range(1, 17)]
RSES_COLS = [f"rses_i{i:02d}" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Data")
    df = df.rename(columns=COV_RENAME)
    df["id"] = df["study"].astype(str) + "-" + df["id"].astype(str)
    return df


def edeq_sentinel(item: str) -> int:
    n = int(item.replace("edeq_i", ""))
    return 99 if n in EDEQ_TIMES_ITEMS else 9


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=EDEQ_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    sentinel = long["item"].map(edeq_sentinel)
    long.loc[long["resp"] == sentinel, "resp"] = float("nan")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(OUT_DIR / "contreras_valdez_2022_edeq.csv", index=False)
    print(f"contreras_valdez_2022_edeq.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

    for out_name, item_cols in [
        ("contreras_valdez_2022_bsq", BSQ_COLS),
        ("contreras_valdez_2022_rses", RSES_COLS),
    ]:
        # 8 ("not administered in this study") and 9 (missing) both -> NaN
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long.loc[long["resp"].isin([8, 9]), "resp"] = float("nan")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
