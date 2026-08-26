"""Daderman, Basinska & Kajonius (2023), Mendeley Data -- Negative Acts
Questionnaire-Revised (NAQ-R).

Source: https://data.mendeley.com/datasets/mgwtzjww7g
DOI: 10.17632/mgwtzjww7g
Data: N867_NAQR_age_sex.sav
License: CC BY 4.0

867 respondents completing the 22-item Negative Acts Questionnaire-Revised,
deposited to replicate an item-response-theory study of workplace bullying
risk groups and gender-based response disparities. An IRT paper's own
item-level data, which is about as close to the IRW's purpose as a deposit
gets.

Surfaced by the 2026-08-25 OpenAIRE/Mendeley pass. Note it had previously
been triaged as `worth_retrying` with the reason "item columns appear to hold
text-coded Likert responses rather than numeric codes" -- that was an
artifact of reading the `.sav` with value labels applied, fixed the same day.

Table written
-------------
daderman_2023_naqr   22 NAQ-R items, resp 1-5

Coding notes
------------
* **The file has no identifier column** -- it is a plain 867 x 25 matrix of
  two demographics, the 22 items and a criterion question. One row is one
  respondent, so `id` is the row position (1..867).
* `bullied` is the study's single self-labelling criterion item ("are you
  bullied at work?", 1-5), not part of the NAQ-R. A single item is not a
  scale, so it is carried as a covariate rather than exported as a table of
  its own.
* `Gender_M1F2` is coded 1 = male, 2 = female per its own name; two
  respondents carry a third value, which is kept as stored rather than
  recoded or dropped.
* All 22 items span the NAQ-R's documented 1-5 frequency scale with no
  out-of-range values.
"""

import io
import os

import pandas as pd
import requests

API = "https://data.mendeley.com/public-api/datasets/mgwtzjww7g"
OUTDIR = "irw_output"
ITEMS = [f"naq{i}" for i in range(1, 23)]


def _load() -> pd.DataFrame:
    meta = requests.get(API, timeout=60).json()
    sav = [f for f in meta["files"] if f["filename"].endswith(".sav")]
    assert len(sav) == 1, [f["filename"] for f in meta["files"]]
    raw = requests.get(sav[0]["content_details"]["download_url"], timeout=300,
                       headers={"User-Agent": "Mozilla/5.0 (IRW-research)"})
    raw.raise_for_status()
    return pd.read_spss(io.BytesIO(raw.content), convert_categoricals=False)


def main():
    d = _load()
    missing = [c for c in ITEMS if c not in d.columns]
    assert not missing, missing
    # No identifier column in the deposit; one row is one respondent.
    assert "id" not in d.columns
    d = d.reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"Gender_M1F2": "cov_gender",
                          "Age": "cov_age",
                          "bullied": "cov_self_labelled_bullied"})
    cov_cols = ["cov_gender", "cov_age", "cov_self_labelled_bullied"]

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    assert long["resp"].between(1, 5).all(), (long["resp"].min(), long["resp"].max())
    assert long.groupby("item")["resp"].nunique().min() > 1
    assert not long.duplicated(["id", "item"]).any()

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "daderman_2023_naqr.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
