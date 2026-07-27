#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0129015
# DOI: 10.1371/journal.pone.0129015
# Supporting Information: https://doi.org/10.1371/journal.pone.0129015.s001
#
# Chronic kidney disease patients, N=200. Two raw-item scales:
#   sf36 -- SF-36 health survey (36 items). Exported as section-specific
#     text categories (8 different response formats across sections,
#     which is expected for SF-36 -- e.g. Q1 is a 5-point general-health
#     item, Q3a-j is a 3-point activity-limitation item, Q5a-c is
#     binary). Each section's full category set enumerated before
#     mapping. A few sections had a single stray numeric value mixed
#     into the text categories (Q3 had one 4.0 against a 3-category
#     scale, Q4 had one 3.0 against a binary scale) -- both isolated and
#     out of range for their section, dropped as data-entry errors. Q10's
#     stray 6.0 was kept: it lands exactly on that section's 6th category
#     ("all the time"), matching Q9's identical response format, so it's
#     a legitimate response exported as a raw code rather than text, not
#     an error.
#   bfi -- Big Five Inventory (44 items, the paper's other focal
#     instrument), exported as 5-point Likert text, one shared category
#     set confirmed across all 44 items.
#
# SF36Q*_R (recoded duplicates for reverse-scored items) and all SF_*/
# QOL_*/B5_Open.../SS_*/B5_{trait} aggregate/subscale columns are
# excluded. SS1-5/SE1-8 (13 items) and SF9-19 (11 items) were left out
# entirely -- no variable labels and no identifiable instrument name in
# the paper's available text, so their construct can't be confirmed.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0129015.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Age": "cov_age", "Sex": "cov_sex", "Race": "cov_race",
              "Education": "cov_education", "Employment": "cov_employment",
              "Income": "cov_income", "CKDStage": "cov_ckd_stage"}

MAP_Q1 = {"not good": 1, "fair": 2, "good": 3, "very good": 4, "excellent": 5}
MAP_Q2 = {"much worse now than one year ago": 1, "somewhat worse now than one year ago": 2,
          "about the same": 3, "somewhat better now than one year ago": 4,
          "much better now than one year ago": 5}
MAP_Q3 = {"yes, limited a lot": 1, "yes, limited a little": 2, "no, not limited at all": 3}
MAP_Q4 = {"Yes": 1, "no": 2}
MAP_Q5 = {"Yes": 1, "no": 2}
MAP_Q6 = {"not at all": 1, "slightly": 2, "moderately": 3, "quite a bit": 4, "extremely": 5}
MAP_Q7 = {"none": 1, "very mild": 2, "mild": 3, "moderate": 4, "severe": 5, "very severe": 6}
MAP_Q8 = {"not at all": 1, "a little bit": 2, "moderately": 3, "quite a bit": 4, "extremely": 5}
MAP_Q9 = {"none of the time": 1, "a little of the time": 2, "some of the time": 3,
          "a good bit of the time": 4, "most of the time": 5, "all the time": 6, 6.0: 6}
MAP_Q11 = {"definitely false": 1, "mostly false": 2, "mostly true": 3, "definitely true": 4}
MAP_BFI = {"disagree strongly": 1, "disagree a little": 2, "neither agree nor disagree": 3,
           "agree a little": 4, "agree strongly": 5}

SF36_MAPS = {
    "SF36Q1": MAP_Q1, "SF36Q2": MAP_Q2,
    **{f"SF36Q3{c}": MAP_Q3 for c in "abcdefghij"},
    **{f"SF36Q4{c}": MAP_Q4 for c in "abcd"},
    **{f"SF36Q5{c}": MAP_Q5 for c in "abc"},
    "SF36Q6": MAP_Q6, "SF36Q7": MAP_Q7, "SF36Q8": MAP_Q8,
    **{f"SF36Q9{c}": MAP_Q9 for c in "abcdefghi"},
    "SF36Q10": MAP_Q9,
    **{f"SF36Q11{c}": MAP_Q11 for c in "abcd"},
}
BFI_COLS = [f"B5{i}" for i in range(1, 45)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id", **COV_RENAME})


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    frames = []
    for item, value_map in SF36_MAPS.items():
        s = df[item].map(value_map)
        frames.append(pd.DataFrame({"id": df["id"], "item": item, "resp": s}))
    sf36 = pd.concat(frames, ignore_index=True)
    sf36 = sf36.dropna(subset=["resp"]).reset_index(drop=True)
    sf36["resp"] = sf36["resp"].astype(int)
    sf36 = sf36.merge(df[["id"] + cov_cols], on="id")
    sf36 = sf36[["id", "item", "resp"] + cov_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sf36.to_csv(OUT_DIR / "ibrahim_2015_sf36.csv", index=False)
    print(f"ibrahim_2015_sf36.csv: ids={sf36['id'].nunique()} items={sf36['item'].nunique()} "
          f"resp={sf36['resp'].min()}-{sf36['resp'].max()}")

    bfi = df.melt(id_vars=["id"] + cov_cols, value_vars=BFI_COLS, var_name="item", value_name="resp")
    bfi["resp"] = bfi["resp"].map(MAP_BFI)
    bfi = bfi.dropna(subset=["resp"]).reset_index(drop=True)
    bfi["resp"] = bfi["resp"].astype(int)
    bfi = bfi[["id", "item", "resp"] + cov_cols]
    bfi.to_csv(OUT_DIR / "ibrahim_2015_bfi.csv", index=False)
    print(f"ibrahim_2015_bfi.csv: ids={bfi['id'].nunique()} items={bfi['item'].nunique()} "
          f"resp={bfi['resp'].min()}-{bfi['resp'].max()}")


if __name__ == "__main__":
    convert()
