"""Altman et al. (2020), Mendeley Data -- Cannabis-Associated Problems Questionnaire.

Source: https://data.mendeley.com/datasets/y8wwtmxxzg
DOI: 10.17632/y8wwtmxxzg
Data: MPS(121519).sav
License: CC BY 4.0

4,053 cannabis-using adults answering the 19-item Cannabis-Associated Problems
Questionnaire (CAPQ), deposited alongside a gender-based differential item
functioning analysis of that instrument.

Why this needed a hand
----------------------
Surfaced by an OpenAIRE discovery pass (2026-08-25) -- Mendeley Data has no
discovery connector of its own, so this deposit had never been seen by any
run. The automatic triage read the file but guessed the wrong columns
(reporting 7 items), so it landed in human_assistance; the .sav's own variable
labels make the 19-item CAPQ block unambiguous.

Table written
-------------
altman_2020_capq   19 CAPQ items, resp 0-5

Coding notes
------------
* `resp = 0` is a real scale point, not a missingness sentinel. The .sav's
  own value labels give the full 6-point scale: 0 = "no", 1 = "yes, but only
  once or a very minor problem", 2 = "yes, but only a couple of times or a
  minor problem", 3 = "yes, a few times or moderate problems", 4 = "yes, many
  times or a somewhat serious problem", 5 = "yes, very many times or a serious
  problem". Four corroborating checks: no SPSS user-missing range is declared
  on any CAPQ variable; NaN exists separately on every item (5-33 each), so
  missingness already has its own representation; 0 occurs on all 19 items,
  47-95% each, and its rate tracks item severity the way a problems checklist
  should ("To lose a job" 93.3%, "Medical problems" 94.8% vs "To
  procrastinate" 47.2%, "Memory loss" 51.3%) rather than being isolated to
  one item; and the authors' own `CAPQ_GLOBAL` equals the plain sum of the 19
  raw items on all 3,824 complete cases, including the 3,816 that contain at
  least one zero. The 541 respondents answering 0 to every item carry through
  to `CAPQ_GLOBAL = 0` rather than being dropped, which a missing code could
  not produce.
* `CAPQ_GLOBAL`, `CAPQ_GLOBAL_BC` (a Box-Cox transform of it) and `CAPQ_SF`
  are derived scores and are excluded, as is `Usepermonth_BC`.
* `Consent` and `Mjuseever` are constant (1) -- screening confirmations, not
  responses -- and are not carried.
* `Averagehigh` and `Daysperweek` are continuous use-quantity measures, not
  items of this instrument; they are kept as covariates rather than exported
  as responses.
* One respondent has no case number in the deposit; they are given an id one
  past the observed maximum rather than dropped.
* Item ids are the source column names (`CAPQ1`..`CAPQ19`), which join
  directly to the item stems stored in the .sav's variable labels.
"""

import os
import tempfile

import pandas as pd
import pyreadstat
import requests

FILE_URL = ("https://data.mendeley.com/public-api/datasets/y8wwtmxxzg")
OUTDIR = "irw_output"

ITEMS = [f"CAPQ{i}" for i in range(1, 20)]
COVS = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Race": "cov_race",
    "Education": "cov_education",
    "Survey": "cov_source_survey",
    "Usepermonth": "cov_use_per_month",
    "Daysperweek": "cov_days_per_week",
    "Averagehigh": "cov_average_high",
}


def _download() -> str:
    """Mendeley's public API returns the file list; take the single .sav."""
    meta = requests.get(FILE_URL, timeout=60).json()
    sav = [f for f in meta["files"] if f["filename"].lower().endswith(".sav")]
    assert len(sav) == 1, [f["filename"] for f in meta["files"]]
    path = os.path.join(tempfile.gettempdir(), sav[0]["filename"])
    with open(path, "wb") as fh:
        fh.write(requests.get(sav[0]["content_details"]["download_url"],
                              timeout=300).content)
    return path


def main():
    d, _meta = pyreadstat.read_sav(_download())
    d = d.rename(columns={"Case": "id"})
    # One row (of 4,053) has a blank case number but complete item responses.
    # It is a real respondent, so give it an id past the observed maximum
    # rather than dropping it.
    missing = d["id"].isna()
    assert missing.sum() == 1, missing.sum()
    d.loc[missing, "id"] = d["id"].max() + 1
    assert d["id"].is_unique

    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long["id"] = long["id"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    assert long["resp"].between(0, 5).all()
    assert long.groupby("item")["resp"].nunique().min() > 1
    assert not long.duplicated(["id", "item"]).any()

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "altman_2020_capq.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
