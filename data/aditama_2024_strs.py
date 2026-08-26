"""Aditama, Atmoko & Muslihati (2024), Mendeley Data -- Indonesian
Student-Teacher Relationship Scale.

Source: https://data.mendeley.com/datasets/b4byp3rn7j
DOI: 10.17632/b4byp3rn7j
License: CC BY 4.0

1,927 Indonesian secondary students completing the Student-Teacher
Relationship Scale, deposited alongside a Rasch validation of the Indonesian
version. Found by the 2026-08-26 triage of the educational-measurement term
sweep.

Table written
-------------
aditama_2024_strs   28 items, resp 1-5

Coding notes
------------
* The item columns are named `item_1`..`item_26` plus two more capitalised
  `Item_*`. The case difference is a typo in the source header, not a
  different instrument -- both use the same 1-5 scale -- so the block is
  matched case-insensitively and ships as one 28-item table. Source names are
  kept as `item` values so item text can join back.
* `Number` is the respondent id and is unique across all 1,927 rows.
* `Umur` (age, 12-17) and `Kelas` (school grade, 7-12) are carried as
  covariates.
"""

import io
import os
import re

import pandas as pd
import requests

API = "https://data.mendeley.com/public-api/datasets/b4byp3rn7j"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = {"Umur": "cov_age", "Kelas": "cov_grade"}


def main():
    meta = requests.get(API, timeout=60, headers=UA).json()
    # The deposit also ships Winsteps output (item/person statistics, a
    # Wright map, local-dependence tables). Only "Data Instrumen.xlsx" holds
    # the raw responses.
    xl = [f for f in meta["files"] if f["filename"] == "Data Instrumen.xlsx"]
    assert len(xl) == 1, [f["filename"] for f in meta["files"]]
    raw = requests.get(xl[0]["content_details"]["download_url"], timeout=300, headers=UA)
    raw.raise_for_status()
    d = pd.read_excel(io.BytesIO(raw.content))

    items = [c for c in d.columns if re.match(r"^item_\d+$", str(c), re.I)]
    assert len(items) == 28, (len(items), items)
    assert d["Number"].is_unique
    d = d.rename(columns={"Number": "id"}).rename(columns=COVS)
    cov_cols = [c for c in COVS.values() if c in d.columns]

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    assert long["resp"].between(1, 5).all()
    assert long.groupby("item")["resp"].nunique().min() > 1
    assert not long.duplicated(["id", "item"]).any()

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "aditama_2024_strs.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
