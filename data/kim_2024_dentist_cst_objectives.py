#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XSCXDR
# DOI (data): 10.7910/DVN/XSCXDR
# DOI (paper): 10.3352/jeehp.2024.21.11
# Data: Kim, J.-H., Kim, Y. J., Ma, D.-S., Park, S.-H., Pae, A., et al. (2024).
#   Revised evaluation objectives of the Korean Dentist Clinical Skill Test: a
#   survey study and focus group interviews. Journal of Educational Evaluation
#   for Health Professions, 21, 11. Harvard Dataverse
#   "jeehp-21-11-dataset1.xlsx".
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# ONE output table:
#   kim_2024_dentist_cst_objectives  perceptions of the Korean Dentist Clinical
#     Skill Test's evaluation objectives, 10 numbered statements (q01..q10),
#     1 = strongly disagree ... 5 = strongly agree (deposit header). One blank
#     cell is dropped.
#   Checked: 116 current and 35 former examinees (paper Results; deposit
#     Respondent 1 / 2).
# Covariate: respondent group (current / former examinee). `id` is the
#   deposit's No.
#
# Item text: not shipped -- statements are numbered only in the data file
#   (questionnaire in suppl. .docx), no register row.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KIMCST_RAW", "jeehp-21-11-dataset1.xlsx")
NAME = "kim_2024_dentist_cst_objectives"


def convert():
    raw = pd.read_excel(RAW, header=None)
    assert [int(x) for x in raw.iloc[1, 2:12]] == list(range(1, 11))
    d = raw.iloc[2:].reset_index(drop=True)
    assert len(d) == 151 and d[0].is_unique
    out = pd.DataFrame({"id": d[0].astype(int),
                        "cov_respondent": d[1].map({1: "current examinee", 2: "former examinee"})})
    assert out["cov_respondent"].value_counts().to_dict() == {"current examinee": 116, "former examinee": 35}
    codes = [f"q{i:02d}" for i in range(1, 11)]
    for k, c in enumerate(codes):
        out[c] = pd.to_numeric(d[2 + k], errors="coerce")
    long = out.melt(id_vars=["id", "cov_respondent"], var_name="item", value_name="resp").dropna(subset=["resp"])
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cov_respondent"]]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
