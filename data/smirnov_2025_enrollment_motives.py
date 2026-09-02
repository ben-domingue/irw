#!/usr/bin/env python3
"""Smirnov & Tarasova (2025), PLOS One -- doctoral enrollment motives (Russia).

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0330679
DOI: 10.1371/journal.pone.0330679
Data: S1 Data (journal.pone.0330679.s001, XLSX)
License: CC BY 4.0
Item text: not shipped. The eleven option labels are readable from the column
    names (`motive_career_academic` and so on) but that is a paraphrase, not
    the wording respondents saw: the survey was Russian, and the only place the
    options are printed is Fig 1, a raster image. Recovering verbatim text
    means the figure or the instrument described in the paper's ref. [59].

1,267 doctoral students from a nationwide Russian survey. The deposit's only
raw response block is the enrollment-motives question:

smirnov_2025_enrollment_motives   11 items  0/1

What the items are -- read this before using the table
-----------------------------------------------------
These eleven binary columns are the options of a **single multiple-choice
question**, "What were your goals for enrolling into the doctorate?", dummy
coded 1 = selected, 0 = not selected. They are not eleven separately
administered probes, and a `0` means "did not tick this option", which is
weaker than an explicit "no". The paper itself treats them exactly as eleven
manifest binary indicators -- it fits a latent class analysis to them, and
Fig 2 reports the conditional probability of selecting each motive per class --
so the person x binary-indicator structure is the source's own, not an artefact
of this conversion. Flagged here rather than buried: a checklist is a
defensible but borderline fit for the standard, and this note is what lets a
downstream user judge it.

Excluded columns
----------------
`RC1`..`RC6`/`RS5` are the paper's own standardized factor scores of extracted
components ("Six variables were extracted -- standardized factor scores of
components"), `class` is the fitted LCA class assignment and
`lack_of_confidence` another standardized score. All four kinds are derived
quantities, not responses, so none is exported and none is carried as a
covariate.

Response coding
---------------
Every motive column is a clean 0/1 with no missing cells, no third code and no
sentinel. The paper describes no imputation ("imput", "missing data", "MICE",
"LOCF", "mean substitution" all absent from the text).

Item names keep the deposit's own column names, which identify each option
(the source's spelling, including `motive_recieve_degree`, is left as is so the
names match the deposit exactly).

The file has no participant id column, so `id` is the row index.

Covariates: gender, marital status, field of study, mode of study (`form`),
funding (`fee`), whether the university is a leading one, prior trajectory,
employment status, career aspirations, and the binary satisfaction answer.
"""

from __future__ import annotations

import os
import tempfile

import pandas as pd
import requests

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0330679.s001")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "automated_finding")
OUT_DIR = os.path.join(AF_DIR, "irw_output")

OUT_NAME = "smirnov_2025_enrollment_motives"

ITEMS = [
    "motive_recieve_degree", "motive_recieve_diploma", "motive_research_skills",
    "motive_teaching_skills", "motive_keep_topic", "motive_career_academic",
    "motive_career_nonacademic", "motive_travel", "motive_work_university",
    "motive_deferment", "motive_dormitory",
]

COVS = {
    "gender": "cov_gender",
    "marital_status": "cov_marital_status",
    "field_of_study": "cov_field_of_study",
    "form": "cov_study_form",
    "fee": "cov_funding",
    "leading": "cov_leading_university",
    "trajectory": "cov_trajectory",
    "employment_status": "cov_employment_status",
    "career_aspirations": "cov_career_aspirations",
    "satisfaction_binary": "cov_satisfaction",
}
COV_COLS = list(COVS.values())


def fetch() -> str:
    path = os.path.join(tempfile.gettempdir(), "pone.0330679.s001.xlsx")
    if not os.path.exists(path):
        r = requests.get(SRC_URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def convert() -> None:
    d = pd.read_excel(fetch())
    os.makedirs(OUT_DIR, exist_ok=True)

    assert all(c in d.columns for c in ITEMS), "missing motive columns"
    d = d.rename(columns=COVS).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    long = d.melt(id_vars=["id"] + COV_COLS, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert long["resp"].isin([0, 1]).all(), "resp is not 0/1"

    long = long[["id", "item", "resp"] + COV_COLS]
    long.to_csv(os.path.join(OUT_DIR, OUT_NAME + ".csv"), index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
