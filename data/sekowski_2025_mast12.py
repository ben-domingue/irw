"""Multi-Attitude Suicide Tendency Scale and PIES, Polish sample.

Source: Sekowski, Marcin (2025), Harvard Dataverse 10.7910/DVN/HXI9SZ,
CC0 1.0 -- "A 12-Item Version of the Multi-Attitude Suicide Tendency Scale".
607 respondents.

Two instruments ship:

  sekowski_2025_mast   30 items, 1-5  (`MAST_*`)
  sekowski_2025_pies   24 items, 1-5  (`PIES_*`)

The four `SBQ_*` columns are NOT shipped. They are the Suicidal Behaviors
Questionnaire-Revised, whose four items each use a different response format
(observed ranges 0-4, 0-6 and 1-3) because the published instrument asks four
structurally different questions. Four items on three different scales in one
table would make `resp` ambiguous, and splitting them would give four
single-item tables. Left for a person to decide.

Item numbering in both blocks is non-contiguous (`PIES_4`, `PIES_7`,
`PIES_11`, ...) because the deposit keeps the original questionnaire numbers
after item reduction. Preserved as-is.
"""
import os
import re

import pandas as pd
import requests

DOI = "10.7910/DVN/HXI9SZ"
BASE = "https://dataverse.harvard.edu"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
UA = {"User-Agent": "irw-batch/1.0 (research; contact itemresponsewarehouse@stanford.edu)"}

SCALES = {"sekowski_2025_mast": (r"^MAST_\d+$", 30),
          "sekowski_2025_pies": (r"^PIES_\d+$", 24)}
COVARIATES = {"Gender": "cov_gender", "Age": "cov_age",
              "Pers_sit": "cov_personal_situation",
              "Work_sit": "cov_work_situation", "Educat": "cov_education",
              "Pl_Resid": "cov_place_of_residence",
              "Pan_SI": "cov_pandemic_suicidal_ideation"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    meta = requests.get(f"{BASE}/api/datasets/:persistentId/",
                        params={"persistentId": f"doi:{DOI}"},
                        headers=UA, timeout=120).json()
    f = next(x for x in meta["data"]["latestVersion"]["files"]
             if x["dataFile"]["filename"].lower().endswith((".xlsx", ".xls")))
    r = requests.get(f"{BASE}/api/access/datafile/{f['dataFile']['id']}",
                     headers=UA, timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["dataFile"]["filename"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df = pd.read_excel(fetch_raw(path))
    item_cols = {}
    for table, (pat, n) in SCALES.items():
        cols = [c for c in df.columns if re.match(pat, str(c))]
        assert len(cols) == n, f"{table}: expected {n} items, found {len(cols)}"
        item_cols[table] = cols

    sbq = [c for c in df.columns if re.match(r"^SBQ_\d+$", str(c))]
    assert len({(df[c].dropna().min(), df[c].dropna().max()) for c in sbq}) > 1, \
        "SBQ items now share one response format; reconsider shipping them"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = [v for v in COVARIATES.values() if v in df.columns]
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
