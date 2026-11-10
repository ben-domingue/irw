#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/3NVNBU
# DOI (data): 10.7910/DVN/3NVNBU
# DOI (paper): 10.3352/jeehp.2024.21.1
# Data: Sohn, C., Kwon, S., Kim, W. G., Lee, K.-E., Lee, S.-Y., & Lee, S.
#   (2024). Importance, performance frequency, and predicted future
#   importance of dietitians' jobs by practicing dietitians in Korea: a survey
#   study. Journal of Educational Evaluation for Health Professions, 21, 1.
#   Harvard Dataverse "jeehp-21-01-dataset1.xlsx" (sheet "all responses";
#   row 1 = codes, row 2 = Korean task names, data from row 4).
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Checked against the paper: 350 practicing dietitians, 98% female (343) --
#   reproduces.
#
# THREE output tables, the same 27 dietitian tasks rated three ways on
#   5-point scales (paper, Methods):
#   sohn_2024_dietitian_importance  P2B2..P2B28, 1 = very unimportant ...
#     5 = very important.
#   sohn_2024_dietitian_frequency  P3B2..P3B28, 1 = do not perform at all ...
#     5 = perform very frequently.
#   sohn_2024_dietitian_future  P4B2..P4B28, 1 = will become very unimportant
#     ... 5 = will become very important in the future.
#   Item codes are the deposit's own; within a table B<k> is the same task
#   across the three tables (task names in row 2 of the sheet).
# Covariates: age, sex, years as a dietitian, years at current workplace,
#   workplace type, region, employment type, education (Korean labels as
#   deposited; the free-text "other" follow-ups and the licence checklist are
#   not carried).
# `id` is the row index (the response ID column is the survey platform's).
#
# Item text: NOT SHIPPED. The Korean task names are the sheet's second
#   header row (study-authored job-analysis tasks); left for a later pass.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SOHN_RAW", "jeehp-21-01-dataset1.xlsx")
COVS = {"P5B2": "cov_age", "P5B3": "cov_sex", "P5B4": "cov_years_dietitian", "P5B5": "cov_years_current_job",
        "P5B6": "cov_workplace", "P5B7": "cov_region", "P5B8": "cov_employment", "P5B9": "cov_education"}
TABLES = {"P2": "sohn_2024_dietitian_importance", "P3": "sohn_2024_dietitian_frequency",
          "P4": "sohn_2024_dietitian_future"}


def convert():
    raw = pd.read_excel(RAW, header=None)
    codes = raw.iloc[0].tolist()
    d = raw.iloc[3:].reset_index(drop=True)
    d.columns = [c if isinstance(c, str) else f"_x{i}" for i, c in enumerate(codes)]
    assert len(d) == 350
    assert (d["P5B3"] == "여").sum() == 343
    d["id"] = range(1, len(d) + 1)
    for src, dst in COVS.items():
        v = d[src]
        d[dst] = v.map(lambda x: x.strip() if isinstance(x, str) else x)
    covs = list(COVS.values())
    os.makedirs(OUT_DIR, exist_ok=True)
    for part, name in TABLES.items():
        items = [f"{part}B{k}" for k in range(2, 29)]
        assert all(c in d.columns for c in items)
        long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}, set(long["resp"])
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
