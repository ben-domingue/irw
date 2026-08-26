"""Milson (2026), York St John University -- problematic social media use,
body satisfaction and self-esteem in sexual and gender minority young adults.

Source: https://yorksj.figshare.com/articles/dataset/_/32113705
DOI: 10.25421/yorksj.32113705
Data: Probelmatic Social Media Use, Body Satisfaction and Self-Esteem Dataset.xlsx
License: CC BY 4.0

A cross-sectional survey of 904 sexual and gender minority young adults.
Recovered 2026-08-25 from the candidate pool that had been unintentionally
blocklisted by `googlesheet_humaneye.csv`.

Tables written
--------------
milson_2026_self_esteem        10 Rosenberg items,       1-4
milson_2026_social_media_use    9 items,                 0-4
milson_2026_body_satisfaction   6 items,                 1-9

Coding notes
------------
* **No identifier column is usable.** `Code_Name` holds self-generated
  participant codes ("Wi03", "La24" -- the usual initials-plus-digits
  construction), and it repeats: 816 distinct over 904 rows. `ID` has only 60
  distinct values. So `id` is the row position, and `Code_Name` is dropped
  rather than carried -- it is pseudonymous rather than anonymous, being
  derived from the participant's own details, and nothing needs it.
* **Free-text identity fields are not exported.** `Gender_6_TEXT` (47 distinct
  self-descriptions) and `Ethnicity_Text` are dropped; on a 904-person
  minority sample, free-text self-description is a meaningful
  re-identification surface and adds nothing an analyst needs. The coded
  `Gender`, `Sexuality`, `Ethnicity` and `Identity` categories are carried as
  covariates, as the deposit publishes them.
* The body-satisfaction block is a **9-point** scale, uniformly 1-9 on all
  six items -- not the 7-point scale a truncated first look suggested.
* `SE_Total`, `SM_Total` and `BS_Total` are derived scale scores and are
  excluded.
* Item labels are kept in source form, including the source's own spelling
  ("Rosenburg"), so item text joins back to the file as published.
"""

import io
import os
import re

import pandas as pd
import requests

FILES_API = "https://api.figshare.com/v2/articles/32113705/files"
OUTDIR = "irw_output"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}

BLOCKS = [
    (re.compile(r"^Rosenburg_esteem_\d+$"),  "self_esteem",       10, (1, 4)),
    (re.compile(r"^Social_media_use_+\d+$"), "social_media_use",   9, (0, 4)),
    (re.compile(r"^BS\d+$"),                 "body_satisfaction",  6, (1, 9)),
]

COVS = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Sexuality": "cov_sexuality",
    "Ethnicity": "cov_ethnicity",
    "Identity": "cov_identity",
}


def _load() -> pd.DataFrame:
    files = requests.get(FILES_API, timeout=60, headers=UA).json()
    xl = [f for f in files if f["name"].lower().endswith((".xlsx", ".xls"))]
    assert len(xl) == 1, [f["name"] for f in files]
    raw = requests.get(xl[0]["download_url"], timeout=300, headers=UA)
    raw.raise_for_status()
    return pd.read_excel(io.BytesIO(raw.content))


def main():
    d = _load()
    # Neither Code_Name (816 distinct of 904) nor ID (60) identifies a person.
    assert d["Code_Name"].duplicated().any() and d["ID"].nunique() < len(d)
    d = d.reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns=COVS)
    cov_cols = [c for c in COVS.values() if c in d.columns]

    os.makedirs(OUTDIR, exist_ok=True)
    for pat, suffix, n_expected, (lo, hi) in BLOCKS:
        items = [c for c in d.columns if pat.match(str(c))]
        assert len(items) == n_expected, (suffix, len(items), items)

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(lo, hi).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"milson_2026_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
