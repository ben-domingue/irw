#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/0XDXKS
# DOI (data): 10.7910/DVN/0XDXKS
# DOI (paper): 10.3352/jeehp.2021.18.23
# Data: Felthun, J. Z., Taylor, S., Shulruf, B., & Allen, D. W. (2021).
#   Empirical analysis comparing the tele-objective structured clinical
#   examination and the in-person assessment in Australia. Journal of
#   Educational Evaluation for Health Professions, 18, 23. Harvard Dataverse
#   "jeehp-18-23-dataset1. Results of 2 OCSE examinations of medical students
#   in the University of New South Wales, Australia in 2019 and 2020".
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# ONE output table:
#   felthun_2021_teleosce  final-year UNSW medicine OSCE: 7 stations (Psych,
#     Emerg, O&G, Pcare, Med, Surg, Paed) x 5-6 domain criteria = 39 items,
#     item = deposit column name with spaces/& made code-safe;
#     "Family & psychology background" ships as Family_psych_history (the
#     covariate linter reads "_background" as a covariate name). UNSW grades
#     fail / borderline / clear pass / distinction are stored as marks
#     3 / 5 / 7 / 9 (same scheme as chong_2018_osce_examiner); resp recodes
#     them 0-3, resp_raw keeps the mark. Blank cells (criteria not assessed at
#     a station sitting) are dropped.
#   Checked: YEAR 0 = 280 rows = 2019 in-person, YEAR 1 = 285 rows = 2020
#     teleOSCE, as in the paper. IDs are unique across both years.
# Covariates: year, assessment mode (in-person / teleOSCE).
#
# Item text: not shipped -- domain names only.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("FELTHUN_RAW", "jeehp-18-23-dataset1.xlsx")
NAME = "felthun_2021_teleosce"
MARK = {3: 0, 5: 1, 7: 2, 9: 3}
COVS = ["cov_year", "cov_mode"]


def code(c):
    c = c.replace("&", "and")
    c = re.sub(r"^(Psych|Emerg|OandG|Pcare|Med|Surg|Paed)", r"\1_", c)
    c = c.replace("Family & psychology background", "Family_psych_history").replace(
        "Family and psychology background", "Family_psych_history")
    return re.sub(r"[^A-Za-z0-9_]+", "_", c).strip("_")


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (565, 41) and d["ID"].is_unique
    assert d["YEAR"].value_counts().to_dict() == {1: 285, 0: 280}
    d["id"] = d["ID"]
    d["cov_year"] = d["YEAR"].map({0: 2019, 1: 2020})
    d["cov_mode"] = d["YEAR"].map({0: "in-person", 1: "teleOSCE"})
    items = list(d.columns[2:41])
    long = d[["id"] + COVS + items].melt(id_vars=["id"] + COVS, var_name="item", value_name="resp_raw")
    long = long.dropna(subset=["resp_raw"])
    long["resp_raw"] = long["resp_raw"].astype(int)
    assert set(long["resp_raw"]) <= set(MARK)
    long["resp"] = long["resp_raw"].map(MARK)
    long["item"] = long["item"].map(code)
    assert long["item"].nunique() == 39
    long = long[["id", "item", "resp", "resp_raw"] + COVS]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3] for c in long["item"].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
