#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/PBNE4K
# DOI (data): 10.7910/DVN/PBNE4K
# DOI (paper): 10.3352/jeehp.2018.15.17
# Data: Chong, L., Taylor, S., Haywood, M., Adelstein, B.-A., & Shulruf, B.
#   (2018). Examiner seniority and experience are associated with bias when
#   scoring communication, but not examination, skills in objective structured
#   clinical examinations in Australia. Journal of Educational Evaluation for
#   Health Professions, 15, 17. Harvard Dataverse "Jeehp_15_17_raw data_Data
#   JEEHP Examiner study__17-07-18" (de-identified).
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# ONE output table:
#   chong_2018_osce_examiner  UNSW undergraduate-medicine OSCE, 2014 and 2016:
#     517 students x 6 stations x 9 criteria (4 generic communication, 3
#     history-taking, 2 physical examination; paper Methods), each station
#     marked by a single examiner. item = "S<station>_I<criterion>" (54 items).
#     Grades were fail / borderline pass / clear pass / distinction, stored as
#     marks 3 / 5 / 7 / 9 (paper); resp recodes them 0-3 and resp_raw keeps
#     the mark. rater = Examiner.ID (237 examiners).
#   Checked: 517 students, 237 examiners, 6 stations each, as in the paper.
# Covariates: cohort (deposit code 0/1, unlabeled -- the two years 2014/2016,
#   order not documented, so it ships as the raw code).
# Dropped: examiner characteristics (gender, experience, clinician, academic,
#   tutor, specialty, rank). They describe the rater, not the student, and
#   datastandard has no rater-covariate column.
#
# Item text: not shipped -- criteria are numbered only.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CHONG_RAW", "Jeehp_15_17_raw data_Data JEEHP Examiner study__17-07-18.xlsx")
NAME = "chong_2018_osce_examiner"
MARK = {3: 0, 5: 1, 7: 2, 9: 3}


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (3102, 23)
    assert d["NAME.ID"].nunique() == 517 and d["Examiner.ID"].nunique() == 237
    assert not d.duplicated(["NAME.ID", "OSCE.Station"]).any()
    d["id"] = d["NAME.ID"]
    d["rater"] = d["Examiner.ID"]
    d["cov_cohort"] = d["Cohort"]
    items = [f"Item{i}" for i in range(1, 10)]
    long = d[["id", "OSCE.Station", "rater", "cov_cohort"] + items].melt(
        id_vars=["id", "OSCE.Station", "rater", "cov_cohort"], var_name="crit", value_name="resp_raw")
    long = long.dropna(subset=["resp_raw"])
    long["resp_raw"] = long["resp_raw"].astype(int)
    assert set(long["resp_raw"]) <= set(MARK)
    long["resp"] = long["resp_raw"].map(MARK)
    long["item"] = "S" + long["OSCE.Station"].astype(str) + "_I" + long["crit"].str.replace("Item", "")
    long = long[["id", "item", "resp", "resp_raw", "cov_cohort", "rater"]]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3] for c in long["item"].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
