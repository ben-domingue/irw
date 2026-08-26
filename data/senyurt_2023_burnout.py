"""Senyurt & Kocabas (2023), Mendeley Data -- burnout in Turkish healthcare
professionals during COVID-19.

Source: https://data.mendeley.com/datasets/dkv4dyxdwx
DOI: 10.17632/dkv4dyxdwx
Data: RawData.xlsx
License: CC BY 4.0

198 Turkish healthcare workers (physicians, nurses and others) completing a
10-item burnout scale, collected as the quantitative half of a mixed-method
study alongside semi-structured interviews. Surfaced by the 2026-08-25
OpenAIRE/Mendeley pass.

Table written
-------------
senyurt_2023_burnout   10 items, resp 1-7

Coding notes
------------
* The deposit ships only the raw data, no instrument document, so the scale is
  described here by its structure rather than named: ten items on a 1-7
  frequency scale. (A 10-item 1-7 burnout measure in a healthcare sample is
  consistent with the Burnout Measure Short version, but nothing in the
  deposit confirms that, so it is not asserted.)
* Every item spans 1-7 except `Burnout1` and `Burnout2`, where no respondent
  used 1. That is a floor of the observed data, not a different scale -- 2-7
  on two items and 1-7 on the other eight, with no out-of-range values
  anywhere.
* The file also carries `Q1`-`Q13`, Turkish yes/no questions about pandemic
  working conditions, and several free-text columns. These are individual
  questions rather than a scored instrument, so they are not exported as an
  IRW table -- the same call made for `reuter_2021_campuslife`. The free-text
  columns were scanned for identifiers (long digit strings, emails, dates):
  none present.
* **Covariates are deliberately limited to gender, age, profession and
  marital status.** The file also has `City` (54 values) and `Expertise` (74
  medical specialties) for 198 respondents; at that granularity the pair is a
  meaningful re-identification surface for a small professional population, so
  neither is carried. `Unnamed: 1` is a constant consent confirmation and is
  dropped.
"""

import io
import os

import pandas as pd
import requests

API = "https://data.mendeley.com/public-api/datasets/dkv4dyxdwx"
OUTDIR = "irw_output"

ITEMS = [f"Burnout{i}" for i in range(1, 11)]
COVS = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Meslek": "cov_profession",
    "Medeni Durum": "cov_marital_status",
}


def _load() -> pd.DataFrame:
    meta = requests.get(API, timeout=60).json()
    xl = [f for f in meta["files"] if f["filename"].endswith(".xlsx")]
    assert len(xl) == 1, [f["filename"] for f in meta["files"]]
    raw = requests.get(xl[0]["content_details"]["download_url"], timeout=300,
                       headers={"User-Agent": "Mozilla/5.0 (IRW-research)"})
    raw.raise_for_status()
    return pd.read_excel(io.BytesIO(raw.content))


def main():
    d = _load().rename(columns={"Participant Number": "id"})
    assert d["id"].is_unique
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    assert long["resp"].between(1, 7).all(), (long["resp"].min(), long["resp"].max())
    assert long.groupby("item")["resp"].nunique().min() > 1
    assert not long.duplicated(["id", "item"]).any()

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "senyurt_2023_burnout.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
