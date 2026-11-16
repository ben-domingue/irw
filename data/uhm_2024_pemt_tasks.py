#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/BSUYWS
# DOI (data): 10.7910/DVN/BSUYWS
# DOI (paper): 10.3352/jeehp.2024.21.13
# Data: Uhm, T., Choi, H., Hong, S. H., Kim, H., Kang, M., Kim, K., et al.
#   (2024). Development of examination objectives for the Korean paramedic and
#   emergency medical technician examination: a survey study. Journal of
#   Educational Evaluation for Health Professions, 21, 13. Harvard Dataverse
#   "jeehp-21-13-dataset1.xlsx" (responses) and "jeehp-21-13-dataset2.xlsx"
#   (task list with means).
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# Job-analysis survey: 448 qualified paramedics (199) and EMTs (249) rated
# each of 253 task elements on frequency, importance and difficulty, each on a
# 6-point scale (1 = 0-10% ... 6 = 91-100%, paper Methods). THREE output
# tables, one per rating dimension (same task set, different question):
#   uhm_2024_pemt_frequency, uhm_2024_pemt_importance, uhm_2024_pemt_difficulty
#   item = T001..T253 in deposit column order (the header carries the task
#   element name, truncated and repeated in places, so it is not a usable key).
#   14 out-of-range cells across all three (7, 13, 14, 15, 23, 25, 31, 35, 43,
#   56, 65, 66 -- isolated entry errors) are dropped; counts printed.
#   Checked: N = 448, 199 paramedics / 249 EMTs, as in the paper.
# Covariates: age, gender (stray trailing space in 3 "M " cells stripped),
#   occupation, certificate year, experience band, work station.
# Dropped: questionnaire number (설문지 번호). `id` is the deposit's Number.
#
# Item text: not shipped -- task element names are in the header and in
#   dataset 2, but there is no register row for this job-analysis survey.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("UHM_RAW", "jeehp-21-13-dataset1.xlsx")
COVS = ["cov_age", "cov_gender", "cov_occupation", "cov_certificate_year", "cov_experience",
        "cov_work_station"]
DIMS = ["Frequency", "Importance", "Difficulty"]


def convert():
    raw = pd.read_excel(RAW, header=None)
    assert raw.shape == (451, 767)
    dims = raw.iloc[2, 8:].tolist()
    assert dims == DIMS * 253
    d = raw.iloc[3:].reset_index(drop=True)
    assert len(d) == 448 and d[0].is_unique
    out = pd.DataFrame({"id": d[0].astype(int)})
    out["cov_age"] = pd.to_numeric(d[2], errors="coerce")
    out["cov_gender"] = d[3].astype(str).str.strip().map({"M": "male", "F": "female"})
    out["cov_occupation"] = d[4].map({1: "paramedic", 2: "EMT"})
    assert out["cov_occupation"].value_counts().to_dict() == {"EMT": 249, "paramedic": 199}
    out["cov_certificate_year"] = pd.to_numeric(d[5], errors="coerce")
    out["cov_experience"] = d[6]
    out["cov_work_station"] = d[7]
    for k, dim in enumerate(DIMS):
        cols = list(range(8 + k, 767, 3))
        sub = d[cols].apply(pd.to_numeric, errors="coerce")
        sub.columns = [f"T{i:03d}" for i in range(1, 254)]
        wide = pd.concat([out, sub], axis=1)
        long = wide.melt(id_vars=["id"] + COVS, var_name="item", value_name="resp").dropna(subset=["resp"])
        bad = ~long["resp"].isin([1, 2, 3, 4, 5, 6])
        name = f"uhm_2024_pemt_{dim.lower()}"
        print(f"{name}: dropping {bad.sum()} out-of-range cells")
        long = long[~bad]
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + COVS]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5, 6] for c in sub.columns})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
