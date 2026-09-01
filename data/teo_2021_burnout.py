#!/usr/bin/env python3
"""Teo et al. (2021), PLOS ONE -- burnout in Singapore allied health professionals.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0244338
DOI: 10.1371/journal.pone.0244338
Data: S1 Data (journal.pone.0244338.s001, XLSX)
License: CC BY 4.0
Item text: not shipped. Both instruments are Mind Garden's licensed
    MBI toolkit -- the MBI-HSS(MP) and the Areas of Worklife Survey -- and
    neither the deposit nor the article reproduces any item wording (the
    Methods name only the subscale structure and the anchors). The text is in
    the published instruments, which are not open, so recovering it needs a
    Mind Garden licence rather than another pass over this source.

329 allied health professionals at a Singapore tertiary hospital, surveyed
October-December 2019. Two instruments, so two tables:

teo_2021_burnout    22 items  mbi_1-mbi_22  0-6  MBI-HSS(MP)
teo_2021_worklife   28 items  aws_1-aws_28  1-5  Areas of Worklife Survey

Response coding, per the Methods
--------------------------------
* MBI: "rate on a Likert scale of 0 (never) to 6 (every day)". All 22 columns
  are integers 0-6 with no missing cells; `0` is the scale's own "never"
  anchor, not a sentinel.
* AWS: "rate on a Likert scale of 1 (strongly disagree) to 5 (strongly agree)".
  All 28 columns are integers 1-5 with no missing cells.

Nothing is filtered: there are no out-of-range values, no blank cells and no
sentinel codes in either block. The paper describes no imputation ("imput",
"missing data", "MICE", "LOCF", "mean substitution" all absent from the text);
it says 17 of 345 questionnaires were excluded for incomplete entries, i.e.
deletion. The deposit carries 329 rows where the paper analyses 328 -- one row
more than the reported analysis sample, with no column marking which is extra,
so all 329 are kept.

Excluded columns
----------------
The deposit ships the authors' derived variables alongside the raw items:
`EE`/`DP`/`PA` subscale sums, `EE_DP_combined` and the `*.number.factor` /
`*.clean.factor` recodings of them, the six `AWS_*_ext.avg` domain means, and
`revaws_*`, the reverse-scored copies of the eight negatively worded AWS items.
None is a response, so none is exported; the raw `aws_*` values are shipped as
stored, un-reversed.

A third instrument, the 27-item PBPT, was administered as an optional
component but is not in the deposit.

Covariates take the deposit's own `*.clean.factor` label strings where it has
them, which is every sociodemographic except age. `age` is a banded code (2-6)
that neither the file nor the paper labels -- the paper's own groupings
(21-30 / 31-40 / 40+) are three, not five -- so it ships as the raw band code
under `cov_age_band` rather than under a guessed set of boundaries.
"""

from __future__ import annotations

import os
import tempfile

import pandas as pd
import requests

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0244338.s001")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "automated_finding")
OUT_DIR = os.path.join(AF_DIR, "irw_output")

COVS = {
    "residency.clean.factor": "cov_residency",
    "gender.clean.factor": "cov_gender",
    "ethnicity.clean.factor": "cov_ethnicity",
    "caregiver.clean.factor": "cov_caregiver",
    "earnings.clean.factor": "cov_earnings",
    "hospital.clean.factor": "cov_hospital",
    "occupation.clean.factor": "cov_occupation",
    "years.clean.factor": "cov_years_experience",
    "position.clean.factor": "cov_position",
    "employment.clean.factor": "cov_employment",
    "nights.clean.factor": "cov_night_shifts",
    "physical_activity.clean.factor": "cov_physical_activity",
    "mental_illness.clean.factor": "cov_mental_illness",
    "mental_help.clean.factor": "cov_mental_help",
    "age": "cov_age_band",
}
COV_COLS = list(COVS.values())

# table -> (column prefix, n items, valid range)
TABLES = [
    ("teo_2021_burnout", "mbi_", 22, (0, 6)),
    ("teo_2021_worklife", "aws_", 28, (1, 5)),
]


def fetch() -> str:
    path = os.path.join(tempfile.gettempdir(), "pone.0244338.s001.xlsx")
    if not os.path.exists(path):
        r = requests.get(SRC_URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def convert() -> None:
    d = pd.read_excel(fetch())
    os.makedirs(OUT_DIR, exist_ok=True)

    d = d.rename(columns=COVS)
    d["id"] = d["record_id"].astype(int)
    assert d["id"].is_unique, "record_id is not unique"

    for out_name, prefix, n, (lo, hi) in TABLES:
        items = [f"{prefix}{i}" for i in range(1, n + 1)]
        assert all(c in d.columns for c in items), f"{out_name}: missing columns"

        long = d.melt(id_vars=["id"] + COV_COLS, value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert long["resp"].between(lo, hi).all(), \
            f"{out_name}: resp outside {lo}-{hi}"

        long = long[["id", "item", "resp"] + COV_COLS]
        long.to_csv(os.path.join(OUT_DIR, out_name + ".csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
