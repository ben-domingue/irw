"""Jordanian Diabetic Health Literacy Questionnaire.

Source: Al-Qerem, Walid (2024), Zenodo 10.5281/zenodo.10812303, CC BY 4.0.
Single file `Data for submission.sav`, 400 respondents x 13 columns: seven
questionnaire items on a 1-5 scale plus six demographics.

The seven item codes are inconsistently cased in the source (`N1`, `N2`, `N3`,
`N5`, `c1`, `c2`, `C3`). They are upper-cased here so the item set is stable,
and the gap at `N4` is left as it stands -- the deposit ships no such column,
and inventing a renumbering would break the join to the source's own labels.
"""
import os

import pandas as pd
import pyreadstat
import requests

RECORD = 10812303
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "alqerem_2024_diabetic_health_literacy"

ITEMS = ["N1", "N2", "N3", "N5", "c1", "c2", "C3"]
COVARIATES = {"Age": "cov_age", "sex": "cov_sex", "education": "cov_education",
              "status": "cov_status", "income": "cov_income",
              "insurance": "cov_health_insurance"}


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
    df, _meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)

    unaccounted = [c for c in df.columns
                   if c not in ITEMS and c not in COVARIATES]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=ITEMS,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["item"] = long["item"].str.upper()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 7
    assert long["resp"].between(1, 5).all(), "expected a 1-5 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
