#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248591
# DOI: 10.1371/journal.pone.0248591
# Tuason, Guss & Boyd (2021), "Thriving during COVID-19: Predictors of
# psychological well-being and ways of coping", PLOS ONE. CC BY 4.0. N=938.
#   Enjoy_*:  author-created COVID-coping checklist ("what do you enjoy in
#             your current situation"), 23 binary yes/no items
#   Lonel_Emo_1-3 / Lonel_Social_1-3: De Jong Gierveld & Van Tilburg
#             Loneliness Scale, emotional/social subscales, 3 items each,
#             text response ("Yes"/"More or less"/"No")
#   WB1-8:    8-item psychological well-being scale, 7-point items --
#             coded 18-24 in the raw file (an internal/Qualtrics offset,
#             not 1-7), kept as-is since only the direction of each item
#             matters, not the absolute starting integer
#   S_Agency_1-6: Sense of Agency Scale, 9-point items, coded 97-105 in the
#             raw file for the same reason as WB above
# "_rec" columns (reverse-coded duplicates of WB/S_Agency) and "_Total"/
# "_Mn"/"_overall" columns (derived composites) are excluded.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0248591.s002

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "irw-batch/1.0 (research)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0248591.s002"

LONEL_MAP = {"No": 0, "More or less": 1, "Yes": 2}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"Age": "cov_age", "Gender": "cov_gender", "Country": "cov_country"})


def _ship(df, item_cols, out_name, recode=None):
    cov_cols = ["cov_age", "cov_gender", "cov_country"]
    df = df.copy()
    df["id"] = range(1, len(df) + 1)
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    if recode:
        long["resp"] = long["resp"].astype(str).map(recode)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(path, index=False)
    print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    enjoy_cols = [c for c in df.columns if c.startswith("Enjoy_") and c != "Enjoy_Open"]
    wb_cols = [f"WB{i}" for i in range(1, 9)]
    sa_cols = [f"S_Agency_{i}" for i in range(1, 7)]

    _ship(df, enjoy_cols, "tuason_2021_covid_coping_enjoy")
    _ship(df, ["Lonel_Emo_1", "Lonel_Emo_2", "Lonel_Emo_3"], "tuason_2021_loneliness_emotional", LONEL_MAP)
    _ship(df, ["Lonel_Social_1", "Lonel_Social_2", "Lonel_Social_3"], "tuason_2021_loneliness_social", LONEL_MAP)
    _ship(df, wb_cols, "tuason_2021_wellbeing")
    _ship(df, sa_cols, "tuason_2021_sense_of_agency")


if __name__ == "__main__":
    convert()
