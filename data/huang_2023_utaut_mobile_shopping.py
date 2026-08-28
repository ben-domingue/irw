"""UTAUT2 mobile-shopping questionnaire.

Source: Tianyang Huang (2023), figshare 10.6084/m9.figshare.24811462,
CC BY 4.0 -- "Research questionnaire data", supporting PLOS ONE 10.1371/
journal.pone.0295581. 389 respondents x 37 items on a 1-7 scale.

The items are the UTAUT2 constructs, each column carrying its construct prefix
and a running number: PE (performance expectancy), EE (effort expectancy),
SI (social influence), FC (facilitating conditions), HM (hedonic motivation),
PV (price value), HA (habit), BI (behavioural intention), UB (use behaviour),
UT (trust), AN (anxiety), TR (perceived risk). They ship as one table -- one
questionnaire, one 1-7 response format -- with the construct kept as
`itemcov_construct`.

Nine cells hold a 0 on a 1-7 scale, and all nine sit in the three price-value
items (`PV117`, `PV218`, `PV319`, three each). Confined to one construct and
absent from the other 34 items, that is a not-applicable code rather than a
response, so those cells are dropped.
"""
import os
import re

import pandas as pd
import requests

ARTICLE = 24811462
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "huang_2023_utaut_mobile_shopping"

ITEM_RE = re.compile(r"^(PE|EE|SI|FC|HM|PV|HA|BI|UB|UT|AN|TR)\d+$")
COVARIATES = {"gender38": "cov_gender", "AgeRange39": "cov_age_range",
              "Education40": "cov_education",
              "PhoneExperience41": "cov_phone_experience",
              "MobileShoppingExperience42": "cov_mobile_shopping_experience"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    meta = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                        timeout=120).json()
    f = next(x for x in meta["files"]
             if x["name"].lower().endswith((".csv", ".xlsx")))
    r = requests.get(f["download_url"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["name"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    p = fetch_raw(path)
    df = pd.read_csv(p) if p.lower().endswith(".csv") else pd.read_excel(p)

    items = [c for c in df.columns if ITEM_RE.match(str(c))]
    assert len(items) == 37, f"expected 37 UTAUT2 items, found {len(items)}"
    accounted = set(items) | set(COVARIATES) | {"Number"}
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)

    bad = ~long["resp"].between(1, 7)
    if bad.any():
        affected = sorted(long.loc[bad, "item"].unique())
        assert all(a.startswith("PV") for a in affected), \
            f"out-of-range values outside the price-value block: {affected}"
        print(f"  dropping {int(bad.sum())} not-applicable cell(s) on {affected}")
        long = long[~bad]

    long["itemcov_construct"] = long["item"].str.extract(r"^([A-Z]{2})")[0]
    long = long[["id", "item", "resp", "itemcov_construct"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 37
    assert long["resp"].between(1, 7).all()

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
