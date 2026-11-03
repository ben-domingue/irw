#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0201919
# DOI: 10.1371/journal.pone.0201919
# Paper: Kozuh, I., Krajnc, R., Hadjileontiadis, L. J., & Debevc, M. (2018).
#   Assessment of problem solving ability in novice programmers. PLOS ONE
#   13(9): e0201919.
# Data: journal.pone.0201919.s002 (S1 Dataset, "Dataset of collected data",
#   .sav), 945 Slovenian primary-school pupils in grades 4-6 taking an
#   elective computer/programming (Scratch) course. S1 Appendix (s001) is
#   the questionnaire; S1-S11 Figs are the task figures.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# THREE output tables:
#   kozuh_2018_programming_tasks   Q18-Q25: eight multiple-choice Scratch
#       programming tasks (series of statements, loops, if-clauses,
#       variables; Piagetian preoperational vs concrete-operational
#       versions). resp = the deposit's own scoring (Qnn_recoded, 0 wrong /
#       1 correct); resp_raw = the option chosen (1-4, or 5 = "not know",
#       which the deposit scores 0). The crosstab of raw vs recoded is
#       checked: exactly one option is scored correct per task.
#   kozuh_2018_course_attitudes    Q5a-Q5j (10 items), 1 strongly disagree ..
#       5 strongly agree: classroom experience (fun, educational,
#       understandable, difficult, successful), attitude toward the course
#       and the teacher, classmates useful / a burden, parents' support. As
#       deposited -- Q5f (difficult) and Q5i (classmates a burden) are NOT
#       reversed; the deposit's *_recoded copies are dropped.
#   kozuh_2018_programming_motivation Q7a-Q7e (5 items), same 1-5 scale:
#       "Motivation to learn programming: attitude 1-5". As deposited; the
#       deposit's reversed copies Q7b_recoded / Q7c_recoded are dropped.
#
# Not shipped: Q9-Q17 (3-option forced choices on desire/effort with
# item-specific, partly unordered options; Q13 is a two-way goal choice),
# Q4 and Q6 (reasons/intentions, nominal), their free-text "other" fields
# (Q4_6_text, Q6_4_text -- children's reasons, screened: no names), and the
# derived sums Q30-Q35, Q6_new, Q6_new2, Q4_recoded*.
#
# Covariates: grade (4/5/6), gender, and which year the pupil is taking the
# course (first/second/third), all from the .sav's value labels.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. The .sav's variable labels are short English
#   descriptors ("Task 1 - series of statements - preoperational",
#   "Classroom experience Q: fun"), not the Slovene items as administered;
#   the English questionnaire is S1 Appendix (journal.pone.0201919.s001)
#   and the task stems depend on the S1-S11 figures.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KOZUH_RAW", "journal.pone.0201919.s002.sav")
N_ROWS = 945
TASKS = [f"Q{i}" for i in range(18, 26)]
LIKERT = {"course_attitudes": ["Q5a", "Q5b", "Q5e", "Q5f", "Q5g", "Q5c", "Q5d", "Q5h", "Q5i", "Q5j"],
          "programming_motivation": ["Q7a", "Q7b", "Q7c", "Q7d", "Q7e"]}


def finish(long, items, scale, name, extra=()):
    long = long[["id", "item", "resp", *extra, "cov_grade", "cov_gender", "cov_course_year"]]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: scale for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    return len(long)


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert txt == ["Q4_6_text", "Q6_4_text"]
    vl = meta.variable_value_labels
    df["id"] = range(1, N_ROWS + 1)
    df["cov_grade"] = df["Q2"].map({1.0: 4, 2.0: 5, 3.0: 6})
    df["cov_gender"] = df["XSPOL"].map(vl["XSPOL"])
    df["cov_course_year"] = df["Q3"].map(vl["Q3"])
    covs = ["cov_grade", "cov_gender", "cov_course_year"]
    assert df[covs].notna().all().all()
    total = 0
    # tasks: resp = deposit's 0/1 scoring, resp_raw = option chosen
    for q in TASKS:
        ct = pd.crosstab(df[q], df[q + "_recoded"])
        assert (ct[1.0] > 0).sum() == 1 and ct.loc[5.0, 1.0] == 0, q
    raw = df[["id"] + covs + TASKS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp_raw")
    sc = df[["id"] + [q + "_recoded" for q in TASKS]].rename(columns={q + "_recoded": q for q in TASKS})
    sc = sc.melt(id_vars=["id"], var_name="item", value_name="resp")
    long = raw.merge(sc, on=["id", "item"], validate="1:1")
    assert long[["resp", "resp_raw"]].notna().all().all()
    long["resp"] = long["resp"].astype(int)
    long["resp_raw"] = long["resp_raw"].astype(int)
    total += finish(long, TASKS, [0, 1], "kozuh_2018_programming_tasks", extra=("resp_raw",))
    for suffix, items in LIKERT.items():
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        total += finish(long, items, [1, 2, 3, 4, 5], f"kozuh_2018_{suffix}")
    not_shipped = [c for c in meta.column_names if not (c in TASKS or c in sum(LIKERT.values(), []))]
    expected = ({q + "_recoded" for q in TASKS} | {"Q2", "XSPOL", "Q3", "Q4", "Q4_recoded", "Q4_6_text",
                "Q5f_recoded", "Q5i_recoded", "Q6", "Q6_4_text", "Q7b_recoded", "Q7c_recoded", "Q30", "Q31",
                "Q32", "Q33", "Q34", "Q35", "Q6_new", "Q6_new2", "Q4_recoded_new"}
                | {c for c in meta.column_names if c[:3] in ("Q9", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15",
                                                            "Q16", "Q17") or c[:2] == "Q9"})
    assert set(not_shipped) == expected, set(not_shipped) ^ expected
    print(f"total responses {total}; {len(not_shipped)} source columns not shipped (see header)")


if __name__ == "__main__":
    convert()
