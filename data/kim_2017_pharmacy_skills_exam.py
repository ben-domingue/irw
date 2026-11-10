#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XSF8XW
# DOI (data): 10.7910/DVN/XSF8XW
# DOI (paper): 10.3352/jeehp.2017.14.6
# Data: Kim, J. H., Lee, J.-Y., Lee, Y. S., Yong, C.-S., Han, N., et al.
#   (2017). Attitudes to proposed assessment of pharmacy skills in Korean
#   pharmacist licensure examination. Journal of Educational Evaluation for
#   Health Professions, 14, 6. Harvard Dataverse "jeehp_14_6.xlsx" (Sheet1,
#   Google Forms export).
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# 466 pharmacy faculty, preceptors and 2015 graduates surveyed in 2015 about
# adding a skills test to the Korean pharmacist licensure examination.
# ONE output table:
#   kim_2017_pharmacy_skills_attitude  the 5-point agreement items Q01, Q02,
#     Q031, Q032, Q033, Q04, Q05, answered as Korean text: 전혀 그렇지 않다 = 1
#     (strongly disagree), 그렇지 않다 = 2, 보통이다 = 3, 그렇다 = 4, 매우
#     그렇다 = 5 (strongly agree); resp_raw keeps the text. 7 free-text
#     write-ins in the "other" option ("잘모름", comments) are dropped.
#   HELD, not built here: kim_2017_pharmacy_skills_inclusion. For each of 16 proposed skill areas
#     (Q121-Q126, Q131-Q132, Q141-Q142, Q151-Q152, Q161-Q164) respondents chose
#     one of "include / feasible", "include / not feasible", "exclude /
#     feasible", "exclude / not feasible". Each answer is two binary
#     judgments, so each area ships as two items: <Q>_include (1 = include)
#     and <Q>_feasible (1 = feasible). Splitting one answer into two items is
#     a call datastandard does not cover, so it waits for Ben (hand-off file;
#     the full script is under automated_finding/runs/held/).
#   Not shipped: Q034, Q071-Q11 and Q110 (free text or multi-choice lists),
#     Q06 (timing choice).
# Covariates: age band, sex, respondent group (faculty / preceptor / graduate,
#   21 "(무응답)" left blank), years in post, region; Korean labels translated.
# Dropped: timestamp, consent, sub-field text. `id` is the row index.
#
# Item text: not shipped -- codes only in the data; questionnaire not in the
#   deposit.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KIMPH_RAW", "jeehp_14_6.xlsx")
LIKERT = {"전혀 그렇지 않다.": 1, "그렇지 않다.": 2, "보통이다.": 3, "그렇다.": 4, "매우 그렇다.": 5}
LIKERT_ITEMS = ["Q01", "Q02", "Q031", "Q032", "Q033", "Q04", "Q05"]
COVS = ["cov_age_band", "cov_sex", "cov_respondent_group", "cov_years_in_post", "cov_region"]
AGE = {"20대": "20s", "30대": "30s", "40대": "40s", "50대": "50s", "60대": "60s"}
GROUP = {"졸업생": "graduate", "프리셉터": "preceptor", "교수": "faculty"}
YEARS = {"5년미만": "<5", "5년이상 10년미만": "5-9", "10년이상 15년미만": "10-14",
         "15년이상 20년미만": "15-19", "20년이상": "20+"}
REGION = {"서울/경기": "Seoul/Gyeonggi", "경상권": "Gyeongsang", "전라권 (제주도 포함)": "Jeolla incl. Jeju",
          "충청권": "Chungcheong", "강원권": "Gangwon"}


def save(long, name, permitted):
    long = long[["id", "item", "resp"] + (["resp_raw"] if "resp_raw" in long else []) + COVS]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in long["item"].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    d = pd.read_excel(RAW, sheet_name="Sheet1")
    assert len(d) == 466
    d["id"] = range(1, len(d) + 1)
    d["cov_age_band"] = d["연령"].map(AGE)
    d["cov_sex"] = d["성별"].map({"여": "female", "남": "male"})
    d["cov_respondent_group"] = d["약사구분"].map(GROUP)
    d["cov_years_in_post"] = d["재직기간"].map(YEARS)
    d["cov_region"] = d["지역"].map(REGION)
    assert d[["cov_age_band", "cov_sex", "cov_years_in_post", "cov_region"]].notna().all().all()
    long = d[["id"] + COVS + LIKERT_ITEMS].melt(id_vars=["id"] + COVS, var_name="item", value_name="resp_raw")
    long = long.dropna(subset=["resp_raw"])
    long["resp_raw"] = long["resp_raw"].astype(str).str.strip()
    long["resp"] = long["resp_raw"].map(LIKERT)
    print("likert write-ins dropped:", long["resp"].isna().sum())
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    save(long, "kim_2017_pharmacy_skills_attitude", [1, 2, 3, 4, 5])


if __name__ == "__main__":
    convert()
