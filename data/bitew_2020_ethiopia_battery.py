#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0240914
# DOI: 10.1371/journal.pone.0240914
# Supporting Information: https://doi.org/10.1371/journal.pone.0240914.s001
#
# Raw file has 5 raw-item scales: a 6-item anxiety measure, a 9-item
# self-efficacy measure, the 3-item Oslo Social Support Scale (OSSS-3),
# PHQ-9, and the 12-item List of Threatening Experiences (LTE-Q). All
# *TOT/*T/SESCORE/PHQCAT total/category columns excluded as aggregates.
# ANXIETY/SEFFICA items are text-coded with unusual/abbreviated category
# labels (e.g. "half/more", "right", "very/right") -- the ordinal
# direction below is inferred from label semantics, not confirmed against
# a published scoring key for these exact wordings.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0240914.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_ANXIETY = {"never": 0, "half/more": 1, "mostly": 2, "always": 3}
MAP_SEFFICA = {"never": 0, "sometimes": 1, "right": 2, "very/right": 3}

COV_RENAME = {"GENDER": "cov_gender", "AGE": "cov_age", "RESIDENCE": "cov_residence"}

SCALES_TEXT = {
    "bitew_2020_anxiety": ([f"ANXIETY{i}" for i in range(1, 7)], MAP_ANXIETY),
    "bitew_2020_self_efficacy": ([f"SEFFICA{i}" for i in range(1, 10)], MAP_SEFFICA),
}
SCALES_NUMERIC = {
    "bitew_2020_osss3": [f"OSSS{i}" for i in range(1, 4)],
    "bitew_2020_phq9": [f"PHQ{i}" for i in range(1, 10)],
    "bitew_2020_lte": [f"LTE{i}" for i in range(1, 13)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def write_scale(long: pd.DataFrame, out_name: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"QID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, (item_cols, value_map) in SCALES_TEXT.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = long["resp"].map(value_map)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        write_scale(long[["id", "item", "resp"] + cov_cols], out_name)

    for out_name, item_cols in SCALES_NUMERIC.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        if out_name == "bitew_2020_lte":
            # LTE-Q is a binary yes/no checklist (0/1). A single "2" (1 of
            # 7908 responses, id 143/LTE1) is a data-entry error, not a
            # real third category -- drop it.
            long.loc[long["resp"] == 2, "resp"] = float("nan")
        if out_name == "bitew_2020_osss3":
            # OSSS-3's standard scoring has no 0 category (item 1 is 1-4,
            # items 2-3 are 1-5). Raw "0" responses are rare (2-4 per item
            # out of ~460-470, vs. 87-287 for genuine categories) -- too
            # sparse to be a real lowest anchor, more consistent with a
            # missing/sentinel value than a valid response. No SPSS value
            # labels exist in the source file to confirm either way.
            long.loc[long["resp"] == 0, "resp"] = float("nan")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        write_scale(long[["id", "item", "resp"] + cov_cols], out_name)


if __name__ == "__main__":
    convert()
