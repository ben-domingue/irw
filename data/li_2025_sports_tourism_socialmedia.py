#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0321999
# DOI: 10.1371/journal.pone.0321999
# Supporting Information (S2 File, SPSS data): https://doi.org/10.1371/journal.pone.0321999.s003
#
# Li (2025) "The impact of social media on university students' revisit
# intention in sports tourism: A hybrid method based on SEM and ANN".
# S2 File is an SPSS .sav with 435 valid respondents (paper: "435 valid
# responses" retained from 472 collected) and six 5-point Likert (1=strongly
# disagree .. 5=strongly agree per the embedded SPSS value labels)
# constructs, one file per construct per the "one file per scale" rule:
#   PU    Perceived Usefulness (4 items)
#   PE    Perceived Enjoyment (4 items)
#   IQ    Information Quality (3 items)
#   SAT   Satisfaction (4 items)
#   eWoM  Electronic Word-of-Mouth (6 items)
#   RV    Revisit Intention (3 items, "RI" in the paper's own text)
# All 24 item columns are integer 1-5 with zero missing values; no
# imputation language found in the paper's Methods/Results text.
#
# "index" (source column "序号") is a unique respondent id (435 unique of
# 435 rows). "totalseconds" (源 "所用时间") is whole-survey completion time
# in seconds, not a per-item response time, so it is carried as a named
# covariate cov_completion_time_s rather than `rt`. No PII present (only
# gender/grade/subject/school-level/source-region covariates).

import io
import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = "https://doi.org/10.1371/journal.pone.0321999.s003"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "li_2025_socmedia_usefulness": ["PU1", "PU2", "PU3", "PU4"],
    "li_2025_socmedia_enjoyment": ["PE1", "PE2", "PE3", "PE4"],
    "li_2025_socmedia_infoquality": ["IQ1", "IQ2", "IQ3"],
    "li_2025_socmedia_satisfaction": ["SAT1", "SAT2", "SAT3", "SAT4"],
    "li_2025_socmedia_ewom": ["eWoM1", "eWoM2", "eWoM3", "eWoM4", "eWoM5", "eWoM6"],
    "li_2025_socmedia_revisit": ["RV1", "RV2", "RV3"],
}

COV_RENAME = {
    "Gender": "cov_gender",
    "Grade": "cov_grade",
    "Subject": "cov_subject",
    "School_level": "cov_school_level",
    "Soure": "cov_source_region",
    "totalseconds": "cov_completion_time_s",
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()

    tmp_path = os.path.join(OUT_DIR, "_tmp_li_2025.sav")
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, meta = pyreadstat.read_sav(tmp_path)
    os.remove(tmp_path)

    df = df.rename(columns={"index": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    assert df["id"].nunique() == len(df), "id column is not unique"

    df["totalseconds"] = pd.to_numeric(df["totalseconds"], errors="coerce")

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]
        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
