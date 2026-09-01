#!/usr/bin/env python3
"""Kohlmann et al. (2016), PLOS ONE -- PHQ-9 depressive symptoms in CHD patients.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0156167
DOI: 10.1371/journal.pone.0156167
Data: S1 Data (journal.pone.0156167.s001, semicolon-delimited CSV)
License: CC BY 4.0
Item text: not shipped. The deposit is a bare data matrix with no labels, and
    the article names the nine symptoms only as short tags ("energy, appetite
    change, feelings of failure, trouble concentrating, psychomotor change,
    suicidal ideations"), not as item stems. The wording is the published
    PHQ-9's, and the administration was German (Hamburg), so shipping it would
    mean substituting the English canonical instrument for the German version
    actually used -- deferred rather than guessed. The German PHQ-9 (Gesundheits-
    fragebogen fuer Patienten, Loewe et al.) is where the text is.

1,337 patients with clinically confirmed coronary heart disease, recruited
consecutively between 2011 and 2013 from three sites in Hamburg, Germany: a
large cardiology outpatient centre, the cardiology outpatient clinic and an
inpatient ward of the University Heart Centre.

kohlmann_2016_phq9   9 items  phq9_1-phq9_9  0-3

Reading the file
----------------
S1 Data is semicolon-delimited with a comma decimal separator, which is why an
automatic comma-delimited read produced a single 25-character-wide column. Read
with `sep=";", decimal=","` it is a clean 1337 x 25 matrix.

Response coding
---------------
The PHQ-9 asks how often each symptom has been present over the past two weeks;
the Methods give the four frequency categories as "'not at all'; 'several
days'; 'more than half the days'; 'nearly every day'", i.e. the instrument's
standard 0-3. All nine columns hold only 0, 1, 2, 3 or a blank.

Missing values in this file are a literal space, not an empty cell, so they
survive `read_csv` as the string " " rather than becoming NaN -- they are
coerced and dropped, 124 item cells in all. The paper describes no imputation
("imput", "missing data", "MICE", "LOCF", "mean substitution" all absent from
the text). No sentinel code appears inside the 0-3 range.

The file has no participant id column, so `id` is the row index.

Covariates: age (in years), gender, education level, employment, setting
(1/2, the recruitment site type), the cardiac history flags (previous
infarction, bypass, hypertension, diabetes, dyslipidemia, smoking, obesity,
family history), and two severity gradings -- `ccsc` (Canadian Cardiovascular
Society angina class, 1-4) and `nyha` (New York Heart Association class, 1-4).
`EQ5D_sum` is the EQ-5D utility index, a composite rather than an item
response, so it is carried as a covariate and not melted. All of these use the
same " " missing marker, which becomes NA.
"""

from __future__ import annotations

import os
import tempfile

import pandas as pd
import requests

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0156167.s001")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "automated_finding")
OUT_DIR = os.path.join(AF_DIR, "irw_output")

OUT_NAME = "kohlmann_2016_phq9"
ITEMS = [f"phq9_{i}" for i in range(1, 10)]

COVS = {
    "age": "cov_age",
    "gender": "cov_gender",
    "education_level": "cov_education_level",
    "employed": "cov_employed",
    "setting": "cov_setting",
    "ccsc": "cov_ccs_angina_class",
    "nyha": "cov_nyha_class",
    "EQ5D_sum": "cov_eq5d_index",
    "infarct": "cov_infarct",
    "bypass": "cov_bypass",
    "hypertension": "cov_hypertension",
    "diabetes": "cov_diabetes",
    "dyslipidemia": "cov_dyslipidemia",
    "smoking": "cov_smoking",
    "obesity": "cov_obesity",
    "familiy_history": "cov_family_history",
}
COV_COLS = list(COVS.values())


def fetch() -> str:
    path = os.path.join(tempfile.gettempdir(), "pone.0156167.s001.csv")
    if not os.path.exists(path):
        r = requests.get(SRC_URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def convert() -> None:
    # semicolon-delimited, comma decimal separator, " " for missing
    d = pd.read_csv(fetch(), sep=";", decimal=",", na_values=[" "],
                    skipinitialspace=False)
    os.makedirs(OUT_DIR, exist_ok=True)

    d = d.rename(columns=COVS).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    for c in COV_COLS:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"] + COV_COLS, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    dropped = long["resp"].isna().sum()
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert long["resp"].between(0, 3).all(), "resp outside the PHQ-9 0-3 range"

    long = long[["id", "item", "resp"] + COV_COLS]
    long.to_csv(os.path.join(OUT_DIR, OUT_NAME + ".csv"), index=False)
    print(f"  {OUT_NAME}: dropped {dropped} blank item cell(s)")
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
