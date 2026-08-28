"""WHOQOL-BREF, caregivers in an autism quality-of-life study.

Source: Sireen Alkhaldi (2023), Zenodo 10.5281/zenodo.7852343, CC BY 4.0 --
"Data set Quality of Life Autism". 201 respondents.

Ships the 26 WHOQOL-BREF items on the instrument's 1-5 scale. The source names
its columns by domain and position (`physical1`, `pcychological1`,
`Environmental1`, `Social1`, plus the two general items `Quality` and
`satisfied`) rather than by WHOQOL item number; the numbered English item text
is carried in each column's SPSS label ("3 To what extent do you feel that
physical pain ..."), so the domain is preserved as `itemcov_domain` and the
source names are kept as the item codes.

Five unsuffixed columns -- `physical`, `pcychological`, `Environmental`,
`social`, `Quality_of_life` -- are domain scores, not items. `physical` runs
1.833-4.833 and `pcychological` 1.167-4.333, fractional values no 1-5 item can
take. Dropped. Note `Quality` (an item) and `Quality_of_life` (a score) differ
by suffix alone, so the two are separated explicitly rather than by pattern.

Seven cells across five items hold a 0 on a 1-5 scale, one or two per item.
The WHOQOL-BREF has no zero category, and no item is affected more than twice
out of 201 respondents, so these are dropped as data-entry errors.
"""
import os

import pandas as pd
import pyreadstat
import requests

RECORD = 7852343
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "alkhaldi_2023_whoqol_autism"

DOMAIN_SCORES = ["physical", "pcychological", "Environmental", "social",
                 "Quality_of_life"]
COVARIATES = {"Gender": "cov_gender", "Age": "cov_age",
              "Educational": "cov_education",
              "Social_status": "cov_social_status", "Sick": "cov_currently_sick",
              "health": "cov_health_condition"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    p = fetch_raw(path)
    try:
        df, _m = pyreadstat.read_sav(p, apply_value_formats=False)
    except Exception:
        df, _m = pyreadstat.read_sav(p, apply_value_formats=False,
                                     encoding="latin1")

    items = [c for c in df.columns
             if c not in COVARIATES and c not in DOMAIN_SCORES]
    assert len(items) == 26, f"expected 26 WHOQOL items, found {len(items)}"
    # The domain scores must really be scores, not items we are discarding.
    for c in DOMAIN_SCORES:
        u = df[c].dropna()
        assert (u != u.round()).any() or u.nunique() > 5, \
            f"{c} looks like an item, not a domain score"

    domain_of = {}
    for c in items:
        s = str(c).lower()
        domain_of[c] = ("physical" if s.startswith("physical")
                        else "psychological" if s.startswith("pcychological")
                        else "environmental" if s.startswith("environmental")
                        else "social" if s.startswith("social")
                        else "general")

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)

    bad = ~long["resp"].between(1, 5)
    if bad.any():
        print(f"  dropping {int(bad.sum())} out-of-range cell(s) on "
              f"{sorted(long.loc[bad, 'item'].unique())}")
        long = long[~bad]

    long["itemcov_domain"] = long["item"].map(domain_of)
    long = long[["id", "item", "resp", "itemcov_domain"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 26
    assert long["resp"].between(1, 5).all()

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
