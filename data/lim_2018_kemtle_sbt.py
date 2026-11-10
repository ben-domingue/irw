#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/UUIC8V
# DOI (data): 10.7910/DVN/UUIC8V
# DOI (paper): 10.3352/jeehp.2018.15.33
# Data: Lim, E. Y., Yim, M. K., & Huh, S. (2018). The relationship of
#   examinees' individual characteristics and perceived acceptability of
#   smart device-based testing to test scores on the practice test of the
#   Korea Emergency Medicine Technician Licensing Examination. Journal of
#   Educational Evaluation for Health Professions, 15, 33. Harvard Dataverse
#   "Jeehp_15_33_raw data.xlsx": sheets S1_questionnaire_survey,
#   S2_variables_explain (codebook), S3_practice_test_results.
# License: CC0 1.0, verified via the Dataverse API. Paper CC BY 4.0.
#
# Found 2026-11-10 (lane C) by triaging the Harvard Dataverse JEEHP collection.
#
# Design (paper, Methods): all 569 examinees took a 130-item tablet-based
#   practice KEMTLE (50 multimedia items, then 80 text items, 5 options, one
#   best answer) on 12 Sept 2015; 560 answered the acceptability survey.
#   Checked: 569 examinees and 560 survey respondents reproduce.
#
# THREE output tables:
#   lim_2018_kemtle_form_a / lim_2018_kemtle_form_b  the practice test, 0/1
#     (1 = correct), one table per booklet. The sheet's "Types" column splits
#     examinees into A (rooms 1-10, 284) and B (rooms 11-20, 285), and the
#     two booklets order the items differently (item 5: p = .95 in A, .22 in
#     B; item 6: .07 vs .93), so position k is not the same item across
#     forms and the forms cannot share item codes. Items mm_01..mm_50 are
#     the multimedia block (교시 1) and tx_01..tx_80 the text block (교시 2),
#     in booklet order. cluster_id = testing room ("Lap").
#   lim_2018_sbt_acceptability  31 survey items, 1 = strongly disagree ...
#     5 = strongly agree (paper; its anchor list misprints 5 as "strongly
#     disagree"): P1-P2 proficiency, IS1-IS20 convenience and comparison
#     with paper testing, ComCBT1-6 comparison with desktop CBT, MMI1-3
#     multimedia items (codes and English wording from S2_variables_explain).
#   The survey's ID and the test's Number are different keys and cannot be
#   linked, so the survey is its own table.
# Covariates: none carried. The eight background variables in the survey
#   are numeric codes the deposit does not label.
#
# Item text: NOT SHIPPED. Test items are not in the deposit. The survey
#   statements are in S2 in English, but the survey was given in Korean and
#   the Korean wording is not deposited.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LIM_RAW", "Jeehp_15_33_raw data.xlsx")
SURVEY = ["P1", "P2"] + [f"IS{k}" for k in range(1, 21)] + [f"ComCBT{k}" for k in range(1, 7)] + \
         [f"MMI{k}" for k in range(1, 4)]


def write(long, items, permitted, name):
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    t = pd.read_excel(RAW, sheet_name="S3_practice_test_results", header=None)
    body = t.iloc[4:].reset_index(drop=True)
    assert body.shape == (569, 136)
    codes = [f"mm_{k:02d}" for k in range(1, 51)] + [f"tx_{k:02d}" for k in range(1, 81)]
    items = body.iloc[:, 6:].astype(int)
    items.columns = codes
    # the deposit's own part totals must equal the item sums
    assert (items[codes[:50]].sum(axis=1).values == body.iloc[:, 3].astype(int).values).all()
    assert (items[codes[50:]].sum(axis=1).values == body.iloc[:, 4].astype(int).values).all()
    items.insert(0, "id", body.iloc[:, 0].astype(int).values)
    items.insert(1, "cluster_id", body.iloc[:, 1].astype(int).values)
    form = body.iloc[:, 2].values
    assert items["id"].is_unique
    for f in ["A", "B"]:
        sub = items[form == f]
        assert set(sub["cluster_id"]) == (set(range(1, 11)) if f == "A" else set(range(11, 21)))
        long = sub.melt(id_vars=["id", "cluster_id"], var_name="item", value_name="resp")
        assert set(long["resp"]) <= {0, 1}
        long = long[["id", "item", "resp", "cluster_id"]]
        write(long, codes, [0, 1], f"lim_2018_kemtle_form_{f.lower()}")

    s = pd.read_excel(RAW, sheet_name="S1_questionnaire_survey", header=None)
    sb = s.iloc[3:].reset_index(drop=True)
    assert sb.shape == (560, 40) and sb[0].is_unique
    sv = sb.iloc[:, 1:32].copy()
    sv.columns = SURVEY
    sv.insert(0, "id", range(1, len(sv) + 1))
    long = sv.melt(id_vars="id", var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    write(long[["id", "item", "resp"]], SURVEY, [1, 2, 3, 4, 5], "lim_2018_sbt_acceptability")


if __name__ == "__main__":
    convert()
