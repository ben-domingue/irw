#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0271374
# DOI: 10.1371/journal.pone.0271374
# Supporting Information (used): https://doi.org/10.1371/journal.pone.0271374.s016 (Stata)
#
# 2-wave Young Lives cohort panel (India), round 0/1 -> wave 1/2. The
# companion S1 (Excel) file has these same items but with string values
# truncated at the source to ~8 characters (e.g. "Strongly" with no
# indication of agree/disagree, "Not very" with no "important"/etc
# suffix) -- unusable/ambiguous. S2 (Stata) has the full untruncated
# strings and is used instead. 5 raw-item scales: CHELP01-05 (5 binary
# items, "child helps with X" checklist), PS1-4 and SP1-4 (4-item
# agreement scales), EPREAS1-5 (5-item importance ratings), NPS1-4
# (already numeric 1-4). PA and other single covariate-like columns not
# part of a coherent multi-item scale are not included.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0271374.s016")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_YESNO = {"No": 0, "Yes": 1}
MAP_AGREE4 = {"Strongly disagree": 1, "Disagree": 2, "Agree": 3, "Strongly agree": 4}
MAP_AGREE5 = {"Strongly disagree": 1, "Disagree": 2, "More or less": 3, "Agree": 4,
              "Strongly agree": 5}
MAP_IMPORTANCE = {"Not important at all": 1, "Not very important": 2,
                   "Moderately important": 3, "Important": 4, "Very important": 5}

COV_RENAME = {"male": "cov_male", "hhsize": "cov_household_size"}

SCALES_TEXT = {
    "hoorani_2022_child_help": ([f"CHELP0{i}" for i in range(1, 6)], MAP_YESNO),
    "hoorani_2022_ps": ([f"PS{i}" for i in range(1, 5)], MAP_AGREE4),
    "hoorani_2022_sp": ([f"SP{i}" for i in range(1, 5)], MAP_AGREE5),
    "hoorani_2022_epreas": ([f"EPREAS{i}" for i in range(1, 6)], MAP_IMPORTANCE),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_stata(io.BytesIO(r.content))
    df = df.rename(columns={"CHILDID": "id", **COV_RENAME})
    df["wave"] = df["round"].astype(int) + 1
    return df


def write_scale(long: pd.DataFrame, out_name: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} waves={sorted(long['wave'].unique())}")


def convert():
    df = fetch_data()
    cov_cols = list(COV_RENAME.values())

    for out_name, (item_cols, value_map) in SCALES_TEXT.items():
        long = df.melt(id_vars=["id", "wave"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = long["resp"].map(value_map)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        write_scale(long[["id", "item", "resp", "wave"] + cov_cols], out_name)

    nps_cols = [f"NPS{i}" for i in range(1, 5)]
    long = df.melt(id_vars=["id", "wave"] + cov_cols, value_vars=nps_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    write_scale(long[["id", "item", "resp", "wave"] + cov_cols], "hoorani_2022_nps")


if __name__ == "__main__":
    convert()
