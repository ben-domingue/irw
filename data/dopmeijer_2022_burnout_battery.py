#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0267175
# DOI: 10.1371/journal.pone.0267175
# Supporting Information: https://doi.org/10.1371/journal.pone.0267175.s001
#
# No person-ID column in the raw file -- row index used. (The automated
# triage's dup_id_item flag came from a heuristic id guess on a different
# column; with the row index as id there is no duplication.) Raw file has
# 4 raw-item scales: SenseBelonging_A-F (6 items), UBOS_A_A-O (15 items,
# Dutch Utrecht Burnout Scale - Student), Loneliness_A-K (11 items, De
# Jong Gierveld scale), PerformancePressure_A-L (12 items). A second
# LON1-11 block duplicates the loneliness items but as DERIVED binary
# scoring points ("1 point for loneliness" / "no points"), not raw
# responses -- excluded, along with all *_total/_stand/_recode/Norm*/
# high_*/BurnoutYES columns (aggregates and derived classifications).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0267175.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_SOB = {"Not true at all": 1, "Not true": 2, "Sometimes not true/sometimes true": 3,
           "True": 4, "Completely true": 5}
MAP_UBOS = {"Never": 1, "On occassion : once a year or less": 2,
            "Sometimes : once a month or less": 3, "Regularly : a couple times a month": 4,
            "Often : once a week": 5, "Very often : a couple of times a week": 6,
            "Always : on a daily basis": 7}
MAP_LON = {"No! Totally disagree!": 1, "No": 2, "More or less": 3, "Yes": 4,
           "Yes! Totally agree!": 5}
MAP_PP = {"I never experience this": 1, "I rarely experience this": 2,
          "I experience this sometimes": 3, "This is often my experience": 4,
          "This is very often my experience": 5}

COV_RENAME = {"Gender": "cov_gender", "Faculty": "cov_faculty", "Age": "cov_age"}

SCALES = {
    "dopmeijer_2022_sense_belonging": ([f"SenseBelonging_{c}" for c in "ABCDEF"], MAP_SOB),
    "dopmeijer_2022_ubos": ([f"UBOS_A_{c}" for c in "ABCDEFGHIJKLMNO"], MAP_UBOS),
    "dopmeijer_2022_loneliness": ([f"Loneliness_{c}" for c in "ABCDEFGHIJK"], MAP_LON),
    "dopmeijer_2022_performance_pressure": ([f"PerformancePressure_{c}" for c in "ABCDEFGHIJKL"], MAP_PP),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str],
               value_map: dict, out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    cov_cols = list(COV_RENAME.values())
    for out_name, (item_cols, value_map) in SCALES.items():
        melt_scale(df, cov_cols, item_cols, value_map, out_name)


if __name__ == "__main__":
    convert()
