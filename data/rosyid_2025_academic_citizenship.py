"""Rosyid (2025), Mendeley Data -- academic citizenship behaviour, ethical
leadership and prosocial motivation in Islamic higher education.

Source: https://data.mendeley.com/datasets/dfzf2kxmr3
DOI: 10.17632/dfzf2kxmr3
Data: Riset Rosyid 2023 New.sav
License: CC BY 4.0

189 undergraduates at Universitas Islam Negeri K.H. Abdurrahman Wahid
Pekalongan. Surfaced by the 2026-08-25 OpenAIRE/Mendeley pass.

Tables written
--------------
rosyid_2025_academic_citizenship   10 items, 1-5
rosyid_2025_ethical_leadership     10 items, 1-5
rosyid_2025_prosocial_motivation    5 items, 1-5

Coding notes
------------
* **A small number of cells are mean-imputed and are dropped.** Between 0.2%
  and 0.4% of values in each block are fractional (3.05, 3.36, 3.86, ...)
  where every real response is an integer 1-5 -- the signature of
  mean-substitution for missing answers. Imputed values are not responses, so
  the script sets any non-integer to NA rather than shipping it; that is what
  the small departures from density 1.000 are.
* Block prefixes map to the study's three constructs, named in the deposit's
  own title and description: `SACB` = (student) academic citizenship
  behaviour, `EL` = ethical leadership, `PsM` = prosocial motivation.
* No identifier column exists, so `id` is the row position.
* Source column names are kept as `item` values so item text can join back.
"""

import io
import os
import re

import pandas as pd
import requests

API = "https://data.mendeley.com/public-api/datasets/dfzf2kxmr3"
OUTDIR = "irw_output"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}

BLOCKS = [("SACB", "academic_citizenship", 10),
          ("EL",   "ethical_leadership",   10),
          ("PsM",  "prosocial_motivation",  5)]

COVS = {"Sex": "cov_sex", "Grade": "cov_grade", "Age": "cov_age",
        "PartTime": "cov_part_time_work"}


def _load() -> pd.DataFrame:
    meta = requests.get(API, timeout=60, headers=UA).json()
    sav = [f for f in meta["files"] if f["filename"].endswith(".sav")]
    assert len(sav) == 1, [f["filename"] for f in meta["files"]]
    raw = requests.get(sav[0]["content_details"]["download_url"], timeout=300,
                       headers=UA)
    raw.raise_for_status()
    return pd.read_spss(io.BytesIO(raw.content), convert_categoricals=False)


def main():
    d = _load().reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    present = {k: v for k, v in COVS.items() if k in d.columns}
    d = d.rename(columns=present)
    cov_cols = list(present.values())

    os.makedirs(OUTDIR, exist_ok=True)
    for prefix, suffix, n_expected in BLOCKS:
        items = [c for c in d.columns if re.match(rf"^{prefix}\d+$", str(c))]
        assert len(items) == n_expected, (suffix, len(items))

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        # Mean-imputed cells are the only non-integers here; drop them.
        n_before = len(long)
        long = long[long["resp"] % 1 == 0]
        dropped = n_before - len(long)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(1, 5).all()
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"rosyid_2025_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f} "
              f"({dropped} imputed cells dropped)")


if __name__ == "__main__":
    main()
