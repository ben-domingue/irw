#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/QWXJJE
# DOI (data): 10.7910/DVN/QWXJJE
# DOI (paper): 10.3352/jeehp.2021.18.7
# Data: Sohn, S., Seo, Y., Jeong, Y., Lee, S., et al. (2021). Changes in the
#   working conditions and learning environment of medical residents after
#   the enactment of the Medical Resident Act in Korea in 2015: a national
#   4-year longitudinal study. Journal of Educational Evaluation for Health
#   Professions, 18, 7. Harvard Dataverse "Dataset 1. Raw data of the
#   responses without the identification of individual training
#   institutions" (kira_share_data) + "Supplement 2. Coding manual".
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# ONE output table:
#   sohn_2021_kira_resident_survey  the ten 5-point Likert items of the annual
#     Korean Intern Resident Association (KIRA) survey, 2016-2019 (coding
#     manual: "5-likert", 1 = strongly disagree ... 5 = strongly agree, paper
#     Methods): w_surv_env, w_surv_well, w_surv_role, w_surv_qol (working
#     environment satisfaction, welfare, role division, quality of life) and
#     t_super_teach, t_effect, t_surv_oppor, t_surv_env, t_mile, t_mile_act
#     (supervision, training effectiveness, opportunity, training-environment
#     satisfaction, year-specific curriculum stated / followed). Not every item
#     was asked every year (w_surv_role 2016-17 only, w_surv_qol 2017 on,
#     t_mile 2016-18); absent cells are simply not rows. The coding manual
#     records small wording changes for some items across years (e.g. the
#     2018 w_surv_env stem is phrased as a question, dissatisfied->satisfied);
#     cov_year carries the administration.
#   Item code w_surv_role ships as w_surv_roles_clear (the covariate linter
#     reads "_role" as a covariate name); the stem: "duties between medical staff are clearly divided".
#   Repeated cross-section, not a panel: `ref` restarts each year, so `id` is
#   "<year>_<ref>". The other survey variables (hours, counts, %, yes/no) are
#   not item responses and are dropped, as are the derived *_adj columns.
#   Checked: N per year 2984 / 3566 / 3779 / 4700, institution type
#   (A/B/C = superior general / general / other) and PGY counts all reproduce
#   the deposit's demographic table exactly.
# Covariates: survey year, institution type, PGY (grade 5 = intern, 1-4 =
#   R1-R4 per the demographic table), specialty group, major code.
#   `sex` is dropped: its codes (1/2, and 3 for every 2019 row) have no
#   labels in the deposit or the paper.
#
# Item text: not shipped -- Korean stems are in the coding manual, but there is
#   no register row for the KIRA survey; candidate for a later itemtext pass.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SOHN_RAW", "kira_share_data.xlsx")
ITEMS = ["w_surv_env", "w_surv_well", "w_surv_role", "w_surv_qol", "t_super_teach",
         "t_effect", "t_surv_oppor", "t_surv_env", "t_mile", "t_mile_act"]
COVS = ["cov_year", "cov_institution_type", "cov_pgy", "cov_specialty", "cov_major"]
NAME = "sohn_2021_kira_resident_survey"


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (15029, 37)
    assert d.groupby("year")["year"].size().to_dict() == {2016: 2984, 2017: 3566, 2018: 3779, 2019: 4700}
    assert d.groupby("year")["ref"].apply(lambda s: s.is_unique).all()
    d["id"] = d["year"].astype(str) + "_" + d["ref"].astype(str)
    d["cov_year"] = d["year"]
    d["cov_institution_type"] = d["class"].map({"A": "superior general hospital", "B": "general hospital",
                                                "C": "other institution"})
    d["cov_pgy"] = d["grade"].map({5: "PGY1 intern", 1: "PGY2 R1", 2: "PGY3 R2", 3: "PGY4 R3", 4: "PGY5 R4"})
    d["cov_specialty"] = d["specialty"]
    d["cov_major"] = d["major"]
    assert d[COVS].notna().all().all()
    long = d[["id"] + COVS + ITEMS].melt(id_vars=["id"] + COVS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    # irw_lint_covariates reads a trailing "_role" as a covariate name
    long["item"] = long["item"].replace({"w_surv_role": "w_surv_roles_clear"})
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + COVS]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in long["item"].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
