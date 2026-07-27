#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0213533
# DOI: 10.1371/journal.pone.0213533
# Supporting Information: https://doi.org/10.1371/journal.pone.0213533.s001
#
# Automated triage flagged this as low-confidence id mapping; id is
# clean/unique (634/634). Raw file has 4 raw-item scales: Pittsburgh
# Sleep Quality Index components (PSQI, 14 items across 2 sub-blocks with
# different response-category wording), Insomnia Severity Index (ISI, 7
# items -- 1a/1b/1c count as 3), Perceived Stress Scale (PSS-14), and the
# Sleep Condition Indicator (SCI, 8 items -- the paper's focal instrument,
# titled specifically about SCI's item-response properties). Each PSQI/
# ISI/SCI item has its own response-category wording (confirmed
# empirically per column, not assumed uniform); PSS-14 is a uniform 5-pt
# scale. PSS_R4/R5/.../R13 are redundant reverse-coded duplicates of
# specific PSS items, not used. All *_total_score/*_totalscore/*_raw
# columns are aggregates, excluded. Pitts1-4 are clock-time values (not
# ordinal item responses) and are excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0213533.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FREQ4 = {"not during the last month": 0, "less then once a week": 1,
         "once or twice a week": 2, "three or more times a week": 3}

PSQI_MAPS = {
    **{f"PSQI_5{c}": FREQ4 for c in "abcdefghij"},
    "PSQI_6": {"very good": 0, "fairly good": 1, "fairly bad": 2, "very bad": 3},
    "PSQI_7": {"not during the past month": 0, "less than wonce a week": 1,
               "once or twice a week": 2, "three or more times a week": 3},
    "PSQI_8": {"not during the past month": 0, "less than once a week": 1,
               "once or twice a week": 2, "three or more times a week": 3},
    "PSQI_9": {"no problem at all": 0, "only a very slight problem": 1,
               "somewhat of a problem": 2, "a very big problem": 3},
}

SEVERITY5 = {"no problem": 0, "mild": 1, "moderate": 2, "severe": 3, "very severe": 4}
IMPACT5 = {"not at all": 0, "a little": 1, "somewhat": 2, "much": 3, "very much": 4}
ISI_MAPS = {
    "ISI_1a": SEVERITY5, "ISI_1b": SEVERITY5, "ISI_1c": SEVERITY5,
    "ISI_2": {"very satisfied": 0, "satisfied": 1, "neutral": 2,
              "dissatisfied": 3, "very dissatisfied": 4},
    "ISI_3": IMPACT5, "ISI_4": IMPACT5, "ISI_5": IMPACT5,
}

DURATION5 = {"0-15 min": 0, "16-30 min": 1, "31-45 min": 2, "46-60 min": 3, ">60 min": 4}
SCI_MAPS = {
    "SCI_1": DURATION5, "SCI_2": DURATION5,
    "SCI_3": {"0-1 nights": 0, "2 nights": 1, "3 nights": 2, "4 nights": 3, "5-7 nights": 4},
    "SCI_4": {"very poor": 0, "poor": 1, "average": 2, "good": 3, "very good": 4},
    "SCI_5": IMPACT5, "SCI_6": IMPACT5, "SCI_7": IMPACT5,
    "SCI_8": {"I don't have a problem / <1mon": 0, "1-2 mon": 1, "3-6 mon": 2,
              "7-12 mon": 3, ">1 year": 4},
}

MAP_PSS = {"never": 0, "almost never": 1, "sometimes": 2, "fairly often": 3, "very often": 4}
PSS_MAPS = {f"PSS_{i}": MAP_PSS for i in range(1, 15)}

COV_RENAME = {"age": "cov_age", "sex": "cov_sex", "programme": "cov_programme"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id", **COV_RENAME})


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_maps: dict, out_name: str):
    item_cols = list(item_maps.keys())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long.apply(lambda r: item_maps[r["item"]].get(r["resp"]), axis=1)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, PSQI_MAPS, "hellstrom_2019_psqi")
    melt_scale(df, cov_cols, ISI_MAPS, "hellstrom_2019_isi")
    melt_scale(df, cov_cols, SCI_MAPS, "hellstrom_2019_sci")
    melt_scale(df, cov_cols, PSS_MAPS, "hellstrom_2019_pss14")


if __name__ == "__main__":
    convert()
