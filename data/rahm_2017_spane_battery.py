#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0171288
# DOI: 10.1371/journal.pone.0171288
# Supporting Information: https://doi.org/10.1371/journal.pone.0171288.s001
#
# `VP` is not a person id -- it records collection mode (e.g. "Online"),
# identical across hundreds of rows -- row index used instead. SPANE items
# have a parallel `_1M` column (a 1-month follow-up administered to a
# subset, 105/498) already stored wide on the same row -- melted into a
# wave column (1=baseline, 2=1-month) rather than kept as separate items.
# SHS items are a 7-point scale exported with only the two endpoint labels
# as text and the middle as raw numeric strings ("2".."6") -- per-item
# maps built from the actual endpoint wording. Also PANAS-20, SWLS, and
# the Hedonic/Eudaimonic-style HSWBS-6 (using its `_recoded` columns for
# items 3/4, matching the raw file's own reverse-coding).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0171288.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_SPANE = {"very rarely or never": 1, "rarely": 2, "sometimes": 3, "often": 4,
             "very often or always": 5}
MAP_PANAS = {"very slightly or not at all": 1, "a little": 2, "moderately": 3,
             "quite a bit": 4, "extremely": 5}
MAP_SWLS = {"strongly disagree": 1, "disagree": 2, "slightly disagree": 3,
            "neither agree nor disagree": 4, "slightly agree": 5, "agree": 6,
            "strongly agree": 7}
MAP_HSWBS = {"strongly disagree": 1, "disagree": 2, "slightly disagree": 3,
             "slightly agree": 4, "agree": 5, "strongly agree": 6}
MAP_SHS = {
    "SHS_1": {"not a very happy person": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
              "a very happy person": 7},
    "SHS_2": {"less happy": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "more happy": 7},
    "SHS_3": {"not at all": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "a great deal": 7},
    "SHS_4": {"not at all": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "a great deal": 7},
}

COV_RENAME = {"gender": "cov_gender", "age": "cov_age_group", "educationlevel": "cov_education"}
SPANE_ITEMS = [f"SPANE_{i}" for i in range(1, 13)]
PANAS_COLS = [f"PANAS_{i}" for i in range(1, 21)]
SWLS_COLS = [f"SWLS_{i}" for i in range(1, 6)]
HSWBS_COLS = ["HSWBS_1", "HSWBS_2", "HSWBS_3_recoded", "HSWBS_4_recoded", "HSWBS_5", "HSWBS_6"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def write_scale(long: pd.DataFrame, out_name: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def melt_simple(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str],
                 value_map: dict, out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    write_scale(long[["id", "item", "resp"] + cov_cols], out_name)


def convert():
    df = fetch_data()
    cov_cols = list(COV_RENAME.values())

    frames = []
    for wave, suffix in [(1, ""), (2, "_1M")]:
        cols = [f"{item}{suffix}" for item in SPANE_ITEMS]
        sub = df[["id"] + cov_cols + cols].copy()
        sub = sub.rename(columns=dict(zip(cols, SPANE_ITEMS)))
        sub["wave"] = wave
        frames.append(sub)
    spane = pd.concat(frames, ignore_index=True)
    long = spane.melt(id_vars=["id", "wave"] + cov_cols, value_vars=SPANE_ITEMS,
                       var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(MAP_SPANE)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    write_scale(long[["id", "item", "resp", "wave"] + cov_cols], "rahm_2017_spane")

    melt_simple(df, cov_cols, PANAS_COLS, MAP_PANAS, "rahm_2017_panas")
    melt_simple(df, cov_cols, SWLS_COLS, MAP_SWLS, "rahm_2017_swls")
    melt_simple(df, cov_cols, HSWBS_COLS, MAP_HSWBS, "rahm_2017_hswbs")

    shs_long = df.melt(id_vars=["id"] + cov_cols, value_vars=list(MAP_SHS.keys()),
                        var_name="item", value_name="resp")
    shs_long["resp"] = shs_long.apply(lambda r: MAP_SHS[r["item"]].get(r["resp"]), axis=1)
    shs_long = shs_long.dropna(subset=["resp"]).reset_index(drop=True)
    shs_long["resp"] = shs_long["resp"].astype(int)
    write_scale(shs_long[["id", "item", "resp"] + cov_cols], "rahm_2017_shs")


if __name__ == "__main__":
    convert()
