#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XYM7XQ
# DOI (data): 10.7910/DVN/XYM7XQ
# DOI (paper): 10.3352/jeehp.2020.17.24
# Data: Choi, J., Oh, T., Oh, J. S., Lim, W., Lee, J., Han, S. K., Park, Y. S.,
#   Kwon, H. G., & Ahn, C. S. (2020). Importance and utilization frequency of
#   essential competencies of Korean physical therapists. Journal of
#   Educational Evaluation for Health Professions, 17, 24. Harvard Dataverse
#   "Dataset 1. Response data from 299 subjects..xlsx" (Google Forms export;
#   each competency has an "[중요도]" (importance) and a "[활용빈도]"
#   (utilization frequency) column); the deposit's Supplements 1-2 list the
#   competencies in Korean and English.
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper (Table 1): 296 of 299 invited physical therapists
#   consented to the privacy terms and answered; 159 male / 137 female --
#   reproduces. The 3 non-consenting rows (and 4 blank rows) are dropped.
#
# TWO output tables, the same 124 competencies rated two ways on 5-point
#   scales (paper: 1 = not entirely important / very low utilization ...
#   5 = very important / very high utilization):
#   choi_2020_pt_competency_importance  comp_001..comp_124 ([중요도]).
#   choi_2020_pt_competency_frequency   comp_001..comp_124 ([활용빈도]).
#   Codes are the competency's position in the questionnaire (column pairs in
#   order); comp_k is the same competency in both tables.
#   The sheet's last row is a row of column means (no consent answers, every
#   value fractional) and two trailing unnamed columns hold more of the same;
#   both fall away with the consent filter / column selection, and the script
#   asserts no fractional value is left among the 296 respondents.
# Covariates (Korean labels as deposited): sex, age band, education, career
#   band, place of employment, specialty.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Competency names are the column headers (Korean)
#   and the deposit's Supplement 2 (English); left for a later pass.

import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CHOI_RAW", "Dataset 1. Response data from 299 subjects..xlsx")
COVS = {2: "cov_sex", 3: "cov_age_band", 4: "cov_education", 5: "cov_career", 6: "cov_workplace",
        7: "cov_specialty"}


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (303, 258)
    d = d[d.iloc[:, 1] == "동의합니다"].copy()
    assert len(d) == 296 and (d.iloc[:, 2] == "남성").sum() == 159
    cols = list(d.columns[8:256])
    assert len(cols) == 248
    assert all(str(c).startswith('Unnamed') for c in d.columns[256:])
    imp, frq = cols[0::2], cols[1::2]
    assert all("[중요도]" in c for c in imp) and all("[활용빈도]" in c for c in frq)
    assert [c.split("[")[0] for c in imp] == [c.split("[")[0] for c in frq]
    codes = [f"comp_{k:03d}" for k in range(1, 125)]
    d["id"] = range(1, len(d) + 1)
    for i, name in COVS.items():
        d[name] = d.iloc[:, i]
    covs = list(COVS.values())
    os.makedirs(OUT_DIR, exist_ok=True)
    for src, name in [(imp, "choi_2020_pt_competency_importance"), (frq, "choi_2020_pt_competency_frequency")]:
        sub = d[["id"] + covs + src].rename(columns=dict(zip(src, codes)))
        long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp").dropna(subset=["resp"])
        assert (long["resp"] == np.floor(long["resp"])).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in codes})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
