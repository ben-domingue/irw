"""Teacher-assessment items and questionnaire-quality ratings.

Source: Matosas-Lopez, Luis (2024), Zenodo 10.5281/zenodo.15151243,
CC BY 4.0 -- "Dataset on the evaluation of teaching efficiency comparing
Likert-type questionnaires vs BARS". 2,223 students x 18 columns.

Two instruments ship separately, because the respondent is rating two
different objects on the same 1-5 scale:

  matosaslopez_2024_teacher_assessment  10 items rating the *teacher*
  matosaslopez_2024_questionnaire_quality  3 items rating the *questionnaire*
      itself (Ambiguity, Clarity, Precision)

Pooling them would make `resp` mean "how good is my teacher" and "how clear is
this survey" in one column.

`Questionnaire_type` records which instrument the student was given (the
study's Likert vs BARS comparison) and ships as a covariate on both tables --
it is the study's experimental factor, so it belongs with every response.
"""
import os
import re

import pandas as pd
import requests

RECORD = 15151243
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

QUALITY = ["Ambiguity", "Clarity", "Precision"]
COVARIATES = {"Age": "cov_age", "Gender": "cov_gender",
              "University_Id": "cov_university",
              "Questionnaire_type": "cov_questionnaire_type"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"]
             if x["key"].lower().endswith((".xlsx", ".xls", ".csv")))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    p = fetch_raw(path)
    df = pd.read_csv(p) if p.lower().endswith(".csv") else pd.read_excel(p)

    teacher = [c for c in df.columns
               if re.match(r"^Teacher_Assessment_Item\d+$", str(c))]
    assert len(teacher) == 10, f"expected 10 teacher items, found {len(teacher)}"
    assert all(c in df.columns for c in QUALITY), "quality items missing"

    accounted = set(teacher) | set(QUALITY) | set(COVARIATES) | {"User_id"}
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, cols in [("matosaslopez_2024_teacher_assessment", teacher),
                        ("matosaslopez_2024_questionnaire_quality", QUALITY)]:
        long = (df.melt(id_vars=["id"] + covs, value_vars=cols,
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() > 1, table
        assert long["resp"].between(1, 5).all(), f"{table}: expected 1-5"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
