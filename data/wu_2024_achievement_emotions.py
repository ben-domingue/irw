"""Achievement emotions of Chinese secondary EFL learners.

Source: Wu, Yajun (2024), Zenodo 10.5281/zenodo.11095879, CC BY 4.0 --
"Chinese Secondary EFL Learners' Achievement Emotions". 1,460 respondents x
19 items on a 1-5 scale.

The item codes are `VAR{group}{position}` -- `VAR11`..`VAR14`, `VAR21`..`VAR24`,
`VAR31`..`VAR34`, `VAR41`..`VAR43`, `VAR51`..`VAR54`. The leading digit is the
emotion subscale and the trailing digit the item within it; the deposit names
no construct for each group, so the codes are kept verbatim rather than
renamed to guessed emotion labels, and the group is carried as
`itemcov_subscale` so the structure is not lost.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 11095879
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "wu_2024_achievement_emotions"

COVARIATES = {"gender": "cov_gender", "grade": "cov_grade"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"]
             if x["key"].lower().endswith((".sav", ".xlsx", ".csv")))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def read_any(p):
    if p.lower().endswith(".sav"):
        try:
            return pyreadstat.read_sav(p, apply_value_formats=False)[0]
        except Exception:
            return pyreadstat.read_sav(p, apply_value_formats=False,
                                       encoding="latin1")[0]
    return pd.read_csv(p) if p.lower().endswith(".csv") else pd.read_excel(p)


def main(path=None):
    df = read_any(fetch_raw(path))
    items = [c for c in df.columns if re.match(r"^VAR\d\d$", str(c))]
    assert len(items) == 19, f"expected 19 items, found {len(items)}"

    accounted = set(items) | set(COVARIATES) | {"ID"}
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES)
    covs = list(COVARIATES.values())
    df["id"] = df["ID"].astype(int)
    assert df["id"].is_unique, "ID is not one row per respondent"

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long["itemcov_subscale"] = long["item"].str[3]
    long = long[["id", "item", "resp", "itemcov_subscale"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 19
    assert long["resp"].between(1, 5).all(), "expected a 1-5 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
