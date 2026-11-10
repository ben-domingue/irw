#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0319305
# DOI: 10.1371/journal.pone.0319305
# Paper: Su W, Fadzil HM, Rauf RAA (2025). Bridging self-directed
#   learning and competency in interdisciplinary teaching among STEM
#   lecturers: How psychological capital connects. PLOS ONE 20(6): e0319305.
# Data: figshare 10.6084/m9.figshare.28830521 (Wenhao Su), one file,
#   paperdata.sav, 408 rows x 90 columns. SPSS variable labels name each item
#   ("Self-management1"); no value labels and no separate codebook, so the
#   response scales are taken from the paper's Measurements section.
# License: CC BY 4.0 (figshare record).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b recoverable_format: three instruments on 1-5 and 1-6 in one file).
#
# THREE output tables, one per instrument (408 STEM lecturers at seven
# universities in Yunnan, China, online survey Dec 2024 - Jan 2025):
#   su_2025_self_directed_learning  Fisher & King self-directed learning
#       readiness, 29 items: Selfmanagement1-10, Learningdesire1-9,
#       Selfcontrol1-10; "five-point Likert scale ... 1 (Strongly Disagree) to
#       5 (Strongly Agree)".
#   su_2025_interdisciplinary_competency  competency in interdisciplinary
#       teaching (Liang & Li), 26 items: Interdisciplinaryteachingdesign1-7,
#       ...implementation1-8, ...evaluation1-11; 1-5, same anchors.
#   su_2025_psycap  psychological capital (Lorenz et al., PCQ-12), 12 items:
#       Selfefficiency1-3, Hope1-3, Optimism1-3, Resilience1-3; "six-point
#       Likert scale ... 1 (Strongly Disagree) to 6 (Strongly Agree)".
#   Item codes are the deposit's variable names.
#
# Covariates (codes as deposited; the file carries no value labels and the
#   paper's Table 1 gives category names but not codes, so the codes are not
#   mapped): cov_gender, cov_age_band (1-4), cov_teaching_years (1-3),
#   cov_education (1-3), cov_cross_major (any cross-major study, 1/2),
#   cov_title (professional title, 1-4), cov_n_courses (1-3),
#   cov_same_subject (teaches the subject of highest degree, 1/2),
#   cov_understand_interdisc (1-5), cov_should_develop (1-5; label "Do you
#   think lecturers should develop competency in interdisciplinary teaching?").
# DROPPED (derived): the 13 subscale / scale means (self_management ..
#   psychological_capital).
# `id`: no id column; row index 1-408.
#
# Imputation: none; no missing cells; every item cell an integer (asserted).
#
# Item text: not shipped -- variable labels are positional ("Self-management1");
#   the stems are not in the deposit or the paper.
#
# PII: none -- all columns are coded demographics, items or means.

import os
import re
import socket
import sys
import tempfile

import pandas as pd
import pyreadstat
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/53847413"
RAW = os.environ.get("SU_STEM_RAW", "")
N_ROWS = 408


def block(prefix, n):
    return [f"{prefix}{i}" for i in range(1, n + 1)]


TABLES = {
    "su_2025_self_directed_learning": (
        block("Selfmanagement", 10) + block("Learningdesire", 9)
        + block("Selfcontrol", 10), 5),
    "su_2025_interdisciplinary_competency": (
        block("Interdisciplinaryteachingdesign", 7)
        + block("Interdisciplinaryteachingimplementation", 8)
        + block("Interdisciplinaryteachingevaluation", 11), 5),
    "su_2025_psycap": (
        block("Selfefficiency", 3) + block("Hope", 3) + block("Optimism", 3)
        + block("Resilience", 3), 6),
}
COVS = {
    "gender": "cov_gender",
    "age": "cov_age_band",
    "teachingyears": "cov_teaching_years",
    "educationalbackground": "cov_education",
    "anyexperiencestudyingacrossdifferentmajorsduringyourhighereducat":
        "cov_cross_major",
    "professionaltitle": "cov_title",
    "Numberofcoursestaughtinthisacademicyear": "cov_n_courses",
    "Isthesubjectyoucurrentlyteachthesameasthesubjectofyourhighestdeg":
        "cov_same_subject",
    "Howwelldoyouunderstandtheconceptofinterdisciplinaryteaching":
        "cov_understand_interdisc",
    "Doyouthinklecturersshoulddevelopcompetency\xa0ininterdisciplinaryt":
        "cov_should_develop",
}
DROPPED = ["self_management", "learning_desire", "self_control",
           "interdiscilinary_teaching_design",
           "interdiscilinary_teaching_implementation",
           "interdiscilinary_teaching_evaluation", "optimisim", "hope",
           "self_efficency", "resilience", "self_directed_learning",
           "competency_in_interdisciplinary_teaching", "psychological_capital"]


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "paperdata.sav")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def convert():
    df, _ = pyreadstat.read_sav(fetch())
    assert df.shape == (N_ROWS, 90), df.shape
    items_all = [c for cols, _ in TABLES.values() for c in cols]
    accounted = set(items_all) | set(COVS) | set(DROPPED)
    assert accounted == set(df.columns), set(df.columns) ^ accounted
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s), all coded demographics: {sorted(strings)}")
    assert set(strings) == set(COVS)
    for c in COVS:
        assert df[c].str.fullmatch(r"\d").all(), c
        df[c] = df[c].astype(int)
    assert int(df.isna().sum().sum()) == 0

    df["id"] = range(1, N_ROWS + 1)
    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, (cols, hi) in TABLES.items():
        assert df[cols].isin(range(1, hi + 1)).all().all(), name
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any()
        constructs = {c: re.sub(r"\d+$", "", c) for c in cols}
        checks = run_qc(long, permitted_values=list(range(1, hi + 1)),
                        item_constructs=constructs)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()}")
    print(f"dropped {len(DROPPED)} derived means; all source columns accounted for")


if __name__ == "__main__":
    convert()
