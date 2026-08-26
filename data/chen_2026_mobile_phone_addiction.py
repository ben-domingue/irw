"""Chen (2026), Harvard Dataverse -- mobile phone addiction, self-control and
social anxiety in Chinese college students.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/QS5D8C
DOI: 10.7910/DVN/QS5D8C
Data: MobilePhoneAddiction-Self-Control.xls.xlsx
License: CC0 1.0

195 college students completing three instruments, deposited for a study of
self-control as a mediator between mobile phone addiction and social anxiety.
Recovered 2026-08-25 from the candidate pool that had been unintentionally
blocklisted by `googlesheet_humaneye.csv`.

Tables written
--------------
chen_2026_mobile_phone_addiction   20 items, 1-5
chen_2026_self_control             19 items, 1-5
chen_2026_social_anxiety           11 items, 1-5

Coding notes
------------
* **`序号` ("serial number") is not a usable identifier** -- 27 of its 195
  values are duplicates, so it is a within-batch sequence rather than a person
  id. One row is one respondent, so `id` is the row position (1..195) and
  `序号` is dropped rather than carried as a covariate.
* The social-anxiety block's first column is headed `7.SA.Q1` where the other
  ten are `7.SA-Q2`..`7.SA-Q11` -- a dot for a hyphen. That is a typo in the
  source header, not a different variable, so the block is matched on a
  pattern that accepts either separator and ships as 11 items.
* All 50 item columns across the three instruments use the same 1-5 scale
  with no out-of-range values.
* Item labels are kept in their source form (including the leading block
  number) so item text can join back to them.
"""

import io
import os
import re

import pandas as pd
import requests

API = ("https://dataverse.harvard.edu/api/datasets/:persistentId/"
       "?persistentId=doi:10.7910/DVN/QS5D8C")
OUTDIR = "irw_output"

# The dot-vs-hyphen typo on 7.SA.Q1 is why these are patterns, not literals.
BLOCKS = {
    "mobile_phone_addiction": (re.compile(r"MPA[.\-]Q\d+$"), 20),
    "self_control":           (re.compile(r"SC[.\-]Q\d+$"),  19),
    "social_anxiety":         (re.compile(r"SA[.\-]Q\d+$"),  11),
}

COVS = {
    "1.Gender": "cov_gender",
    "2.Grade": "cov_grade",
    "3.Major": "cov_major",
    "4.Only-child": "cov_only_child",
    "5.Household registration type": "cov_household_registration",
}


UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}


def _load() -> pd.DataFrame:
    # Harvard Dataverse sits behind a WAF that rejects header-less requests.
    meta = requests.get(API, timeout=60, headers=UA).json()["data"]["latestVersion"]
    xl = [f for f in meta["files"]
          if f["dataFile"]["filename"].endswith((".xlsx", ".xls"))]
    assert len(xl) == 1, [f["dataFile"]["filename"] for f in meta["files"]]
    url = ("https://dataverse.harvard.edu/api/access/datafile/"
           + str(xl[0]["dataFile"]["id"]))
    raw = requests.get(url, timeout=300, headers=UA)
    raw.raise_for_status()
    return pd.read_excel(io.BytesIO(raw.content))


def main():
    d = _load()
    # No usable identifier: 序号 repeats. One row is one respondent.
    assert d["序号"].duplicated().any(), "序号 is unique after all -- use it as id"
    d = d.reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)

    present = {k: v for k, v in COVS.items() if k in d.columns}
    d = d.rename(columns=present)
    cov_cols = list(present.values())

    os.makedirs(OUTDIR, exist_ok=True)
    for name, (pat, n_expected) in BLOCKS.items():
        items = [c for c in d.columns if pat.search(str(c))]
        assert len(items) == n_expected, (name, len(items), items)

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(1, 5).all(), (
            name, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"chen_2026_{name}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
