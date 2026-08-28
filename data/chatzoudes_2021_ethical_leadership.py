"""Ethical leadership and organizational outcomes in hospitality.

Source: Chatzoudes, D. & Theriou, G. (2021), Zenodo 10.5281/zenodo.5646614,
CC BY 4.0 -- "The effect of ethical leadership on organizational outcomes in
the hospitality industry". 503 respondents.

Six constructs ship as six tables. All use the same 1-5 agreement scale, but
they measure six different objects (the leader, the service, the respondent's
own intentions, exhaustion, trust and satisfaction), so one table would make
`resp` ambiguous about what is being rated:

  chatzoudes_2021_ethical_leadership    9 items
  chatzoudes_2021_service_delivery      8 items
  chatzoudes_2021_job_satisfaction      5 items
  chatzoudes_2021_emotional_exhaustion  4 items
  chatzoudes_2021_turnover_intention    3 items
  chatzoudes_2021_trust                 3 items

Each construct also has an unsuffixed summary column (`Ethical_Leadership`
next to `Ethical_Leadership_01`..`_09`, and so on). Those are subscale means
-- `Ethical_Leadership` runs 1.556-5.0 and `Service_Delivery` 2.25-5.0, values
no 1-5 item can take -- and are dropped. Matching items on the construct name
alone rather than on the numeric suffix would have swept all six into the item
sets.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 5646614
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

CONSTRUCTS = {
    "chatzoudes_2021_ethical_leadership": ("Ethical_Leadership", 9),
    "chatzoudes_2021_service_delivery": ("Service_Delivery", 8),
    "chatzoudes_2021_job_satisfaction": ("Job_Satisfaction", 5),
    "chatzoudes_2021_emotional_exhaustion": ("Emotional_exhaustion", 4),
    "chatzoudes_2021_turnover_intention": ("Turnover_Intention", 3),
    "chatzoudes_2021_trust": ("Trust", 3),
}
COVARIATES = {"Sex": "cov_sex", "Age": "cov_age", "Years": "cov_years"}


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

    item_cols, summaries = {}, []
    for table, (stem, n) in CONSTRUCTS.items():
        cols = [c for c in df.columns if re.match(rf"^{stem}_\d+$", str(c))]
        assert len(cols) == n, f"{table}: expected {n} items, found {len(cols)}"
        item_cols[table] = cols
        assert stem in df.columns, f"{stem} summary column missing"
        summaries.append(stem)

    accounted = set(sum(item_cols.values(), [])) | set(summaries) | set(COVARIATES)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, cols in item_cols.items():
        long = (df.melt(id_vars=["id"] + covs, value_vars=cols,
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == len(cols), table
        assert long["resp"].between(1, 5).all(), f"{table}: expected 1-5"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
