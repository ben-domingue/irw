"""Medicine Student Experience Questionnaire (MedSEQ).

Source: Huang & Velan, Harvard Dataverse 10.7910/DVN/SQ8PJY, CC0 1.0 --
"What impacts students' satisfaction the most from Medicine Student Experience
Questionnaire". Single file `jeehp-20-02-dataset1.xlsx`, 1,719 responses x 27
columns; 22 MedSEQ items on a 1-5 agreement scale.

`Q_Satisfaction` is the study's outcome variable (overall satisfaction), not a
MedSEQ item, so it ships as a covariate rather than in the item set.

The file has no respondent identifier and one row per returned questionnaire,
so `id` is the row index.
"""
import os

import pandas as pd
import requests

DOI = "10.7910/DVN/SQ8PJY"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "huang_2023_medseq"

# Harvard Dataverse answers 403 to requests without a User-Agent.
UA = {"User-Agent": "irw-batch/1.0 (research; contact itemresponsewarehouse@stanford.edu)"}

COVARIATES = {"Q_Cohort": "cov_cohort",
              "Q_CampusLocation": "cov_campus",
              "Q_Year": "cov_year",
              "Q_Gender": "cov_gender",
              "Q_Satisfaction": "cov_overall_satisfaction"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    base = "https://dataverse.harvard.edu"
    meta = requests.get(f"{base}/api/datasets/:persistentId/",
                        params={"persistentId": f"doi:{DOI}"},
                        headers=UA, timeout=120).json()
    files = meta["data"]["latestVersion"]["files"]
    f = next(x for x in files
             if x["dataFile"]["filename"].lower().endswith((".xlsx", ".xls")))
    r = requests.get(f"{base}/api/access/datafile/{f['dataFile']['id']}",
                     headers=UA, timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["dataFile"]["filename"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df = pd.read_excel(fetch_raw(path))
    items = [c for c in df.columns if str(c).startswith("MedSEQ_")]
    assert len(items) == 22, f"expected 22 MedSEQ items, found {len(items)}"

    unaccounted = [c for c in df.columns
                   if c not in items and c not in COVARIATES]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() > 1
    assert long["resp"].between(1, 5).all(), "MedSEQ is a 1-5 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
