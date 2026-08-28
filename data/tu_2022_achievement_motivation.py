"""Achievement Motivation Scale, Chinese college students.

Source: Song Tu & Xiao Qingzeng (2022), Zenodo 10.5281/zenodo.7219876,
CC BY 4.0 -- "Measurement of achievement motivation for college students".
Single file `data.sav`, 124,328 respondents x 41 columns; 30 items (`CD1`..
`CD30`) on a 1-4 scale, labelled in the source as 成就动机 (achievement
motivation).

At ~3.7M responses this is one of the largest tables in the IRW.

**`id` is the row index, not the source's `number` column.** `number` looks
like a respondent identifier but is not one: it has 78,728 distinct values
across 124,328 rows. It is a within-school running number -- adding `SCHOOL`
lifts uniqueness to 123,816 and adding `GRADE` to 124,179, still short of the
row count. There are no fully duplicated rows, so each row is a distinct
returned questionnaire and the row *is* the unit. `number` and `SCHOOL` ship
as covariates so the source's own structure is preserved and recoverable.

`AGE` carries 43 impossible values (the maximum is 18,172,860,104), so ages
outside 10-100 are set missing rather than shipped. `ifpoor` is constant at 1
across all 124,328 rows and is dropped.
"""
import os
import re

import numpy as np
import pandas as pd
import pyreadstat
import requests

RECORD = 7219876
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "tu_2022_achievement_motivation"

COVARIATES = {
    "number": "cov_source_number", "GENDER": "cov_gender", "AGE": "cov_age",
    "SCHOOL": "cov_school", "SCHOOLLEVEL": "cov_school_level",
    "GRADE": "cov_grade", "ADRESS": "cov_residence",
    "poortypes": "cov_poverty_type", "ifgetmoney": "cov_receives_aid",
    "livingcost": "cov_living_cost",
}
CONSTANT = ["ifpoor"]


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=900)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
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

    items = [c for c in df.columns if re.match(r"^CD\d+$", str(c))]
    assert len(items) == 30, f"expected 30 items, found {len(items)}"

    accounted = set(items) | set(COVARIATES) | set(CONSTANT)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    for c in CONSTANT:
        assert df[c].nunique(dropna=True) == 1, f"{c} is not constant"

    # The stated reason for not using `number` as the id must still hold.
    assert df["number"].nunique() < len(df), \
        "`number` is now unique; reconsider using it as the id"
    assert not df.duplicated().any(), \
        "fully duplicated rows appeared; the row is no longer one questionnaire"

    df = df.rename(columns=COVARIATES)
    covs = list(COVARIATES.values())
    df["cov_age"] = df["cov_age"].where(df["cov_age"].between(10, 100), np.nan)
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 30
    assert long["resp"].between(1, 4).all(), "the scale is 1-4"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
