#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/F5POU5
# DOI (data): 10.7910/DVN/F5POU5
# DOI (paper): 10.3352/jeehp.2024.21.30
# Data: Thompson, Garg, Shotwell, et al. (2024). Development and validation of
#   a measurement tool to assess student perceptions of using real patients in
#   physical therapy education at the rehabilitation sciences program,
#   University of Texas Medical Branch, the United States. Journal of
#   Educational Evaluation for Health Professions, 21, 30. Harvard Dataverse
#   "jeehp-21-30-dataset.xlsx".
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# ONE output table:
#   thompson_2024_sprp_pte  Student Perceptions of Real Patient Use in
#     Physical Therapy Education (SPRP-PTE), the full 48-item development
#     version: value / satisfaction / confidence x overall (5 items each),
#     cognitive (4), psychomotor (3), affective (4) learning; 4-point
#     agreement scale (paper Methods), 1-4 in the file. The paper's EFA later
#     drops 18 items; all 48 ship. item = <domain>_<construct>_<k>, k the
#     position within the deposit's block (the deposit's own labels repeat
#     "Q3" in the cognitive-satisfaction block, so labels are not used).
#     20 cells hold 0, which is not on the 4-point scale: read as skipped
#     (the paper admits respondents who answered 40 of 48 and imputes
#     nothing) and dropped.
#   Checked: 130 students, as in the paper.
# Covariates: program type (private/public), year in program.
# `id` is the row index (the deposit's first column is blank).
#
# Item text: not shipped -- stems are in the deposit's supplements (.docx),
#   no register row.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("THOMPSON_RAW", "jeehp-21-30-dataset.xlsx")
NAME = "thompson_2024_sprp_pte"
COVS = ["cov_program_type", "cov_program_year"]
DOMAIN = {"Overall Learning": "overall", "Confidence": "overall", "Cognitive": "cognitive",
          "Psychomotor": "psychomotor", "Affective": "affective"}


def code_items(cols):
    out, count = [], {}
    for c in cols:
        s = c.strip()
        dom = next(v for k, v in DOMAIN.items() if s.startswith(k))
        con = ("value" if "Value" in s else "satisfaction" if "Satisfaction" in s else "confidence")
        key = f"{dom}_{con}"
        count[key] = count.get(key, 0) + 1
        out.append(f"{key}_{count[key]}")
    return out


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (130, 101)
    items = [c for c in d.columns if re.search(r"Q\d", str(c))]
    assert len(items) == 48
    codes = code_items(items)
    assert len(set(codes)) == 48
    d["id"] = range(1, len(d) + 1)
    d["cov_program_type"] = d["Private 1/Public 2"].map({1: "private", 2: "public"})
    d["cov_program_year"] = d["Year 1/1, Year 2/2, Year 3/3"]
    sub = d[["id"] + COVS + items].rename(columns=dict(zip(items, codes)))
    long = sub.melt(id_vars=["id"] + COVS, var_name="item", value_name="resp").dropna(subset=["resp"])
    print(f"{NAME}: dropping {(long['resp'] == 0).sum()} zero cells")
    long = long[long["resp"] != 0]
    assert set(long["resp"]) <= {1, 2, 3, 4}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + COVS]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
