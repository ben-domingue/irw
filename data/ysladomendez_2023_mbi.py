"""Maslach Burnout Inventory, Peruvian healthcare professionals.

Source: Yslado-Mendez, R. M., Sanchez-Broncano, J. & De la Cruz-Valdiviano, C.
(2023), Zenodo 10.5281/zenodo.8374494, CC BY 4.0 -- "Psychometric Properties of
the Maslach Burnout Inventory in Healthcare Professionals, Ancash". 303
respondents x 22 MBI items on the instrument's 0-6 frequency scale.

Only the MBI ships. The deposit also carries a 17-item binary block (`A1`..,
plus `A12_A`) and a 10-item 1-5 block (`B1`..`B10`) which are the study's
comparison measures; the record names neither instrument and publishes no
codebook, so they are not shipped under guessed construct names. The presence
of `Anxiety` and `Depression` score columns (both 0-9) suggests one of them is
a screening instrument, but that is an inference from neighbouring columns
rather than a source, so it is recorded rather than acted on.

Eight columns are computed and dropped: `CE`, `DD` and `RP` are the MBI's
emotional-exhaustion, depersonalisation and personal-accomplishment subscale
scores, `BS` the total (1-67, against items that top out at 6), and
`Workplace well-being`, `Anxiety`, `Depression` the other instruments' scores.
Note the collision: `BS` is the burnout total while `BS1`..`BS22` are the
items, so the items are matched on a required numeric suffix.
"""
import os
import re

import pandas as pd
import requests

RECORD = 8374494
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "ysladomendez_2023_mbi"

COVARIATES = {"Age": "cov_age", "Gender": "cov_gender",
              "Marital Status ": "cov_marital_status",
              "Number of children": "cov_n_children",
              "Hospital": "cov_hospital",
              "Employment Status ": "cov_employment_status",
              "Ocupación": "cov_occupation", "Work area": "cov_work_area",
              "Type": "cov_type",
              "Direct care of confirmed COVID-19": "cov_direct_covid_care",
              "Diagnosed with COVID-19 infection": "cov_diagnosed_covid",
              "TS": "cov_ts", "hc": "cov_hc"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"]
             if "mbi" in x["key"].lower() and x["key"].lower().endswith((".xlsx", ".xls")))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df = pd.read_excel(fetch_raw(path))
    # `BS` alone is the burnout total; only BS<digits> are items.
    items = [c for c in df.columns if re.match(r"^BS\d+$", str(c))]
    assert len(items) == 22, f"expected 22 MBI items, found {len(items)}"
    assert "BS" in df.columns and df["BS"].dropna().max() > 6, \
        "the BS total column is missing or no longer a total"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = [v for v in COVARIATES.values() if v in df.columns]
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 22
    assert long["resp"].between(0, 6).all(), "the MBI is a 0-6 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
