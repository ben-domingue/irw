#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0261495
# DOI: 10.1371/journal.pone.0261495
# Paper: Muscio A, Vallanti G (2022). The gender gap in Ph.D.
#   entrepreneurship: How do students perceive the academic environment? PLoS
#   ONE 17(4): e0261495.
# Data: PLOS Supporting Information S1 Data (journal.pone.0261495.s001, Stata
#   .dta with variable labels), 11,835 Ph.D. students admitted 2008-14 at
#   Italian universities, surveyed 2014-15. The survey was administered by
#   CINECA, which removed contact details before the authors received it.
# License: CC BY 4.0 (the article and its SI; the authors deposited the data
#   as SI under the journal's licence).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 4.
#
# FOUR output tables, item codes the deposit's own (its English variable
# labels give each item's topic):
#   muscio_2022_phd_rating      q13a-i, the student's rating of their Ph.D.
#     programme (competence of the supervisor, time for research, equipment,
#     funding, autonomy, international network, international experience,
#     research team, access to the labour market), 1-6.
#   muscio_2022_drivers         q51a-o, "relevance of drivers to
#     entrepreneurship" (public funding, private funding, bank loans, ...,
#     business competition schemes), "1 - absolutely not important" to
#     "6 - absolutely important" (the paper). q51p ("Altro", other) is
#     dropped: it is a write-in slot and carries a 0 code.
#   muscio_2022_obstacles       q52a-l, relevance of obstacles to
#     entrepreneurship (unclear academic rules, raising finance, ..., need
#     for authorisations). The paper describes the same 1-6 scale, but no
#     cell holds 6 across 12 items and ~6,400 respondents, so these items look
#     to have been asked on a 1-5 scale; the codes are kept as given.
#   muscio_2022_university_env  q53a-i, "The student agrees that in the home
#     university (1~6=highest)": a favourable environment to startup
#     creation, ..., professional support to potential entrepreneurs, 1-6.
# Covariates: age, parent is an entrepreneur (0/1), subject area (from the
#   deposit's 14 area dummies; their English labels).
# Dropped: the university-level variables (policies, rating, size, share of
#   women faculty, unemployment rate); the Ph.D.-cohort dummies; the yes/no
#   career items; the risk-preference category (one item). 703 rows answer
#   none of the items and contribute no rows (14 pairs of them are identical
#   all-missing rows).
# `id` is the row index (the deposit has no respondent id).
#
# Item text: NOT SHIPPED. The variable labels hold the English item topics
#   (above); the full Italian wording is not in the SI.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0261495.s001"
RAW = os.environ.get("MUSCIO_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
TABLES = {"phd_rating": ("q13", "_phdgiudizio", "abcdefghi", range(1, 7)),
          "drivers": ("q51", "_driverimp", "abcdefghijklmno", range(1, 7)),
          "obstacles": ("q52", "_ostimp", "abcdefghijkl", range(1, 6)),
          "university_env": ("q53", "_uniimp", "abcdefghi", range(1, 7))}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        src = os.path.join(OUT_DIR, "_muscio_tmp.dta")
        open(src, "wb").write(r.content)
    df, meta = pyreadstat.read_dta(src)
    if not RAW:
        os.remove(src)
    return df, meta


def convert():
    df, meta = load()
    assert df.shape == (11835, 86), df.shape
    print(f"PII screen: {len(df.columns)} columns examined; no names, contacts or free text read")
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_age"] = df["q01_eta"].astype("Int64")
    df["cov_parent_entrepreneur"] = df["q07_genitoreimpr"].astype("Int64")
    areas = [f"area_{i}" for i in range(1, 15)]
    assert (df[areas].sum(axis=1) <= 1).all()
    lab = {a: meta.column_names_to_labels[a].replace("subject - ", "").strip() for a in areas}
    df["cov_subject_area"] = df[areas].idxmax(axis=1).map(lab).where(df[areas].sum(axis=1) == 1)
    covs = ["cov_age", "cov_parent_entrepreneur", "cov_subject_area"]
    for name, (q, suffix, letters, perm) in TABLES.items():
        items = [f"{q}{c}{suffix}" for c in letters]
        assert all(c in df.columns for c in items), name
        sub = df[["id"] + covs + items].rename(columns={c: c[:len(q) + 1] for c in items})
        codes = [c[:len(q) + 1] for c in items]
        long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"])
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(perm), (name, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(perm) for c in codes})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"muscio_2022_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
