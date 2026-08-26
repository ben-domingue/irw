"""Eldor et al. (2022), Frontiers in Psychology -- resilience against
radicalization and extremism in schools.

Source: https://doi.org/10.3389/fpsyg.2022.980180
DOI: 10.3389/fpsyg.2022.980180
Data: Table 3 (frontiersin.figshare.com article 21531195)
License: CC BY 4.0

334 Norwegian school students, deposited as the validation sample for a new
49-item political-resilience scale plus eight convergent-validity measures.
Recovered 2026-08-25 from the candidate pool that had been unintentionally
blocklisted by `googlesheet_humaneye.csv`.

Every measure uses the same 1-7 response scale.

Tables written
--------------
eldor_2022_political_resilience    49 items
eldor_2022_anomie                   7 items
eldor_2022_violent_intentions       7 items
eldor_2022_relative_deprivation     6 items
eldor_2022_school_resilience        5 items
eldor_2022_violent_extremism        5 items
eldor_2022_symbolic_threat          3 items
eldor_2022_realistic_threat         3 items
eldor_2022_collective_anger         3 items

Coding notes
------------
* `ResponseId` is the Qualtrics response identifier and is unique on all 334
  rows, so it is used as `id`. The export carries no IP address, geolocation
  or contact column -- checked, since Qualtrics exports often do.
* `Duration__in_seconds_` is whole-survey completion time, not per-item
  response time, so it is a covariate (`cov_completion_time_s`) and
  explicitly **not** `rt`.
* Excluded as derived or duplicated: the scale scores
  (`safety_connectedness`, `anomi`, `symbolic_threat`, `realistic_threat`,
  `anger`, `RD`, `violent_intentions`, `RIS`, `School_attentiveness`,
  `Equality`, `Risk`, `filter_$`); the stored reverse-scored copies
  `violent_beh_intentio_4r/5r/7r`, whose un-reversed originals are already
  in the block; and `political_resilience_42RC`, a recode of item 42.
* `I_1` is constant (1 for every respondent) and is not exported.
* The source spells one block `colelctive_anger`; the table is named
  `collective_anger` but the source column names are kept as `item` values so
  item text joins back to the file as published.
"""

import io
import os
import re

import pandas as pd
import requests

FILES_API = "https://api.figshare.com/v2/articles/21531195/files"
OUTDIR = "irw_output"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}

# source block prefix -> output table suffix, expected item count
BLOCKS = [
    ("political_resilience", "political_resilience", 49),
    ("anomi",                "anomie",                7),
    ("violent_beh_intentio", "violent_intentions",    7),
    ("relative_deprivation", "relative_deprivation",  6),
    ("school_resilience",    "school_resilience",     5),
    ("violent_extremism",    "violent_extremism",     5),
    ("symbolic_threat",      "symbolic_threat",       3),
    ("realistic_threat",     "realistic_threat",      3),
    ("colelctive_anger",     "collective_anger",      3),
]

COVS = {
    "gender": "cov_gender",
    "ethnicity": "cov_ethnicity",
    "skole": "cov_school",
    "Duration__in_seconds_": "cov_completion_time_s",
}


def _load() -> pd.DataFrame:
    files = requests.get(FILES_API, timeout=60, headers=UA).json()
    xl = [f for f in files if f["name"].upper().endswith((".XLSX", ".XLS"))]
    assert len(xl) == 1, [f["name"] for f in files]
    raw = requests.get(xl[0]["download_url"], timeout=300, headers=UA)
    raw.raise_for_status()
    return pd.read_excel(io.BytesIO(raw.content))


def main():
    d = _load().rename(columns={"ResponseId": "id"})
    assert d["id"].is_unique, "ResponseId is not unique"
    d = d.rename(columns=COVS)
    cov_cols = [c for c in COVS.values() if c in d.columns]

    os.makedirs(OUTDIR, exist_ok=True)
    for prefix, suffix, n_expected in BLOCKS:
        # Plain `<prefix>_<n>` only: this drops the stored reversals (`_4r`)
        # and the recode (`_42RC`), whose originals are already in the block.
        pat = re.compile(rf"^{re.escape(prefix)}_\d+$")
        items = [c for c in d.columns if pat.match(str(c))]
        assert len(items) == n_expected, (prefix, len(items))

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(1, 7).all(), (
            prefix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1, f"{prefix}: constant item"
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"eldor_2022_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
