#!/usr/bin/env python3
"""Shao et al. (2025), PLOS One -- authentic leadership and teacher work engagement.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0320839
DOI: 10.1371/journal.pone.0320839
Data: S1 File (journal.pone.0320839.s001, XLSX)
License: CC BY 4.0
Item text: not shipped. The spreadsheet headers are positional codes
    (`Al1`..`WE9`) with no label row, and the article prints only one example
    item per scale. The wording is in the four published instruments the
    Methods cite -- Walumbwa et al.'s Authentic Leadership Questionnaire
    (Mind Garden, licensed), Johnson et al.'s school climate scale combined
    with Liu et al., the Tschannen-Moran & Hoy TSES short form, and the
    Schaufeli UWES-9 -- so recovering it means going to those, not back to
    this source.

1,034 primary, secondary and high school teachers in a district of Shandong
Province, surveyed 1-15 June 2024 by cluster sampling across eleven schools.
Four instruments in one questionnaire, each on its own response scale, so four
tables:

shao_2025_authentic_leadership  Al1-Al14  14 items  1-5  ALQ (Walumbwa et al.)
shao_2025_school_climate        SC1-SC10  10 items  1-5  Johnson et al. / Liu et al.
shao_2025_teacher_efficacy      TE1-TE12  12 items  1-9  TSES short form
shao_2025_work_engagement       WE1-WE9    9 items  1-7  UWES-9

Response coding, per the Methods
--------------------------------
* ALQ: "The 5-point Likert scale was used, with scores ranging from 1-5
  indicating 'strongly disagree' to 'strongly agree'".
* School climate: "a 5-point Likert scale, ranging from '1-Strongly Disagree'
  to '5-Strongly Agree'".
* TSES: "The ratings on the Likert scale ranged from 1 (none at all) to 9 (a
  great deal)". The data uses all nine points.
* UWES-9: the Methods describe "a 7-point Likert scale, with scores ranging
  from 0 (Never) to 6 (Always)", which is the published UWES coding, but the
  deposit stores the nine WE columns as 1-7, not 0-6 -- the same seven points
  shifted up by one. The values are shipped as stored rather than silently
  subtracted, since which end the shift came from is not recorded anywhere;
  direction and spacing are unaffected.

One cell is dropped: `Al1` holds a single `7` on a 1-5 scale. It is the only
out-of-range value in all 45 item columns and occurs once against 14,476
legitimate ALQ responses -- isolated to one item, so a keying slip rather than
an unnamed sixth or seventh category.

There are no other out-of-range values, no blank cells and no sentinel codes.
The paper describes no imputation ("imput", "missing data", "MICE", "LOCF",
"mean substitution" all absent) and says questionnaires with missing values
were excluded, i.e. deletion. It reports 1,043 valid questionnaires where the
deposit has 1,034 rows; the deposit is what is shipped.

The file has no participant id column, so `id` is the row index.

Covariates: `Gender`, `age` (in years, 22-60), `stage` (school stage, 1-3) and
two columns whose source names are Chinese-derived -- `culture` (文化程度,
education level, 1-4) and `zhicheng` (职称, professional title rank, 1-3).
Both ship under descriptive names; their level codings are not documented in
the deposit or the paper, so the raw codes are kept as stored.
"""

from __future__ import annotations

import os
import tempfile

import pandas as pd
import requests

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0320839.s001")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "automated_finding")
OUT_DIR = os.path.join(AF_DIR, "irw_output")

COVS = {"Gender": "cov_gender", "age": "cov_age", "stage": "cov_school_stage",
        "culture": "cov_education_level", "zhicheng": "cov_professional_title"}
COV_COLS = list(COVS.values())

# table -> (item prefix, n items, valid range)
TABLES = [
    ("shao_2025_authentic_leadership", "Al", 14, (1, 5)),
    ("shao_2025_school_climate", "SC", 10, (1, 5)),
    ("shao_2025_teacher_efficacy", "TE", 12, (1, 9)),
    ("shao_2025_work_engagement", "WE", 9, (1, 7)),
]


def fetch() -> str:
    path = os.path.join(tempfile.gettempdir(), "pone.0320839.s001.xlsx")
    if not os.path.exists(path):
        r = requests.get(SRC_URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def convert() -> None:
    d = pd.read_excel(fetch())
    os.makedirs(OUT_DIR, exist_ok=True)

    d = d.rename(columns=COVS).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    for out_name, prefix, n, (lo, hi) in TABLES:
        items = [f"{prefix}{i}" for i in range(1, n + 1)]
        assert all(c in d.columns for c in items), f"{out_name}: missing columns"

        long = d.melt(id_vars=["id"] + COV_COLS, value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])

        bad = ~long["resp"].between(lo, hi)
        if bad.any():
            print(f"  {out_name}: dropping {int(bad.sum())} out-of-range cell(s) "
                  f"{sorted(long.loc[bad, 'resp'].unique())}")
            long = long[~bad]
        long = long.reset_index(drop=True)

        long = long[["id", "item", "resp"] + COV_COLS]
        long.to_csv(os.path.join(OUT_DIR, out_name + ".csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
