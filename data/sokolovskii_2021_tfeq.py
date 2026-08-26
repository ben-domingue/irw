"""Sokolovskii et al. (2021), figshare -- Three-Factor Eating Questionnaire,
Russian validation.

Source: https://figshare.com/articles/dataset/_/16577462
DOI: 10.6084/m9.figshare.16577462
Data: data_set.xlsx
License: CC BY 4.0

213 university students in Stavropol Krai, Russia, completing the 51-item
Three-Factor Eating Questionnaire for a Russian-language validation study.
Recovered 2026-08-25 from the candidate pool that had been unintentionally
blocklisted by `googlesheet_humaneye.csv`.

Table written
-------------
sokolovskii_2021_tfeq   51 items, resp 1-5

Coding notes
------------
* `ID1` is the respondent identifier and is unique across all 213 rows. The
  other two non-item columns are collection bookkeeping, not identifiers, and
  are dropped: `Скан` ("scan") has 4 values naming data-entry batches, and
  `Номер` ("number") repeats -- only 173 distinct values over 213 rows -- so
  it is a within-batch sequence number, not a person id.
* All 51 items use the same 1-5 response scale with no out-of-range values.
  (The original English TFEQ mixes true/false and 4-point formats; this
  Russian adaptation is uniform, which is what the file shows.)
* No covariates are exported -- the deposit carries none beyond the batch
  bookkeeping above.
"""

import io
import os

import pandas as pd
import requests

FILE_API = "https://api.figshare.com/v2/articles/16577462/files"
OUTDIR = "irw_output"
ITEMS = [f"i_{i}" for i in range(1, 52)]


def _load() -> pd.DataFrame:
    files = requests.get(FILE_API, timeout=60).json()
    # The deposit also ships analysis workbooks (correlations, Cronbach's
    # alpha) and a SEM archive; only data_set.xlsx holds the raw responses.
    xl = [f for f in files if f["name"] == "data_set.xlsx"]
    assert len(xl) == 1, [f["name"] for f in files]
    raw = requests.get(xl[0]["download_url"], timeout=300,
                       headers={"User-Agent": "Mozilla/5.0 (IRW-research)"})
    raw.raise_for_status()
    return pd.read_excel(io.BytesIO(raw.content))


def main():
    d = _load().rename(columns={"ID1": "id"})
    assert d["id"].is_unique, "ID1 is not unique"
    missing = [c for c in ITEMS if c not in d.columns]
    assert not missing, missing

    long = d.melt(id_vars=["id"], value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    assert long["resp"].between(1, 5).all(), (long["resp"].min(), long["resp"].max())
    assert long.groupby("item")["resp"].nunique().min() > 1
    assert not long.duplicated(["id", "item"]).any()

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "sokolovskii_2021_tfeq.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
