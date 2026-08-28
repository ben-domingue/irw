"""Five Personality Factors Test (5PFT), Dutch cohorts 1982-2007.

Source: Wicherts, Jelte (2023), DataverseNL 10.34894/8NGA0R, CC0 1.0 -- data
from "Cohort Differences in Big Five Personality Factors Over a Period of 25
Years". 8,954 administrations x 81 columns; 70 items on a 1-7 scale, 14 per
Big Five factor, each labelled in the source with its trait ("extraversion
item 1", "agreeableness item 1", ...).

One table: the 5PFT is a single inventory with one response format, and the
factor structure is a property of the instrument rather than of the
administration.

`id` is the row index. `TWNO` is labelled "Participant ID no." but resolves
only 8,936 distinct values over 8,954 rows, and pairing it with `Testweek`
does not separate them either -- 18 rows still share a key. Each row is one
completed test, so the row is the unit; `TWNO`, `Testweek` and `COHORT` ship
as covariates so the cohort design stays recoverable.

Six cells hold an 8 on a 1-7 scale, spread over five different items
(`PF27A06`, `PF41E09`, `PF42A09`, `PF53C11` twice, `PF67A14`). One stray value
per item across 8,954 respondents is a data-entry error rather than a
different response format, so those cells are dropped rather than clamped.

The five `*5PFT_val` columns are trait scores and are dropped as composites;
`MIS5PFT` is a per-respondent missingness count and ships as a covariate.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

DOI = "10.34894/8NGA0R"
BASE = "https://dataverse.nl"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "wicherts_2023_5pft"

UA = {"User-Agent": "irw-batch/1.0 (research; contact itemresponsewarehouse@stanford.edu)"}
COVARIATES = {"TWNO": "cov_source_participant_no", "Testweek": "cov_testweek",
              "COHORT": "cov_cohort", "SEX": "cov_sex", "AGE": "cov_age",
              "MIS5PFT": "cov_n_missing_items"}
COMPOSITES = ["E5PFT_val", "V5PFT_val", "G5PFT_val", "N5PFT_val", "O5PFT_val"]


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    meta = requests.get(f"{BASE}/api/datasets/:persistentId/",
                        params={"persistentId": f"doi:{DOI}"},
                        headers=UA, timeout=120).json()
    files = meta["data"]["latestVersion"]["files"]
    f = next(x for x in files
             if x["dataFile"]["filename"].lower().endswith(".sav"))
    r = requests.get(f"{BASE}/api/access/datafile/{f['dataFile']['id']}",
                     headers=UA, timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["dataFile"]["filename"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    src = fetch_raw(path)
    try:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False)
    except Exception:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False,
                                        encoding="latin1")

    items = [c for c in df.columns if re.match(r"^PF\d+[EACNO]\d+$", str(c))]
    assert len(items) == 70, f"expected 70 5PFT items, found {len(items)}"
    per_trait = {}
    for c in items:
        per_trait.setdefault(re.match(r"^PF\d+([EACNO])", c).group(1), []).append(c)
    assert all(len(v) == 14 for v in per_trait.values()), \
        f"expected 14 items per trait, got { {k: len(v) for k, v in per_trait.items()} }"

    accounted = set(items) | set(COVARIATES) | set(COMPOSITES)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES)
    covs = list(COVARIATES.values())
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)

    bad = ~long["resp"].between(1, 7)
    if bad.any():
        print(f"  dropping {int(bad.sum())} out-of-range cell(s) on "
              f"{sorted(long.loc[bad, 'item'].unique())}")
        long = long[~bad]

    long = long[["id", "item", "resp"] + covs]
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 70
    assert long["resp"].between(1, 7).all()

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
