#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/JJ0C6Z
# DOI (data): 10.7910/DVN/JJ0C6Z
# DOI (paper): 10.3389/fpubh.2026.1710189
# Data: Mastrothanasis, K., et al. (2026). Drama-based simulations in first aid
#   education: psychometric validation of the SPRS-S in school settings.
#   Frontiers in Public Health. Harvard Dataverse "datasetfor1710189" (SPSS
#   .sav original).
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 by lane C (sweep 2); built 2026-11-10 (hour-1110-b).
#
# ONE output table:
#   mastrothanasis_2026_sprs_s  Greek Standardized Patient Performance Rating
#     Scale - Student Version (SPRS-S), Q1..Q9: school students rate the
#     simulated patient's (the first-aid instructor's) role-play, 1 = strongly
#     disagree, 2 = disagree, 3 = agree, 4 = strongly agree (paper Methods,
#     four-point scale with faces). The student is `id`; three instructors
#     played the patient, and the deposit identifies them only by gender
#     (cov_instructor_gender), so no rater/target column can be built.
#   Checked: 332 students, 160 boys / 172 girls (paper abstract). No missing.
# Covariates: gender, class (grade 5 to upper-secondary year 3; SPSS value
#   labels), instructor gender. `id` is the row index.
#
# Item text: not shipped -- the .sav has no variable labels for Q1-Q9; the
#   items are in the paper's appendix, no register row.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("MASTRO_RAW", "datasetfor1710189.sav")
NAME = "mastrothanasis_2026_sprs_s"
COVS = ["cov_gender", "cov_class", "cov_instructor_gender"]


def convert():
    d = pd.read_spss(RAW, convert_categoricals=False)
    assert d.shape == (332, 12)
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["Gender"].astype(int)
    d["cov_class"] = d["Class"].astype(int)
    d["cov_instructor_gender"] = d["Teach_Gender"].astype(int)
    assert d["cov_gender"].value_counts().to_dict() == {2: 172, 1: 160}
    items = [f"Q{i}" for i in range(1, 10)]
    long = d[["id"] + COVS + items].melt(id_vars=["id"] + COVS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert set(long["resp"]) <= {1, 2, 3, 4}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + COVS]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
