#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/7QPCVV
# DOI: 10.3352/jeehp.2017.14.14
#   Wormley, M. E., Romney, W., & Greer, A. E. (2017). "Development of the
#   Clinical Teaching Effectiveness Questionnaire in the United States."
#   Journal of Educational Evaluation for Health Professions 14:14.
#   (PMC5676018; the paper's Supplement 1 is this deposit.)
# Data: Dataverse datafile 3031544, "Jeehp_14_14_raw data.xlsx"
#       (format=original; one sheet, 205 rows x 71 columns; US physical
#       therapy clinical instructors, SurveyMonkey, 2015).
# License: CC0 1.0 (Dataverse dataset licence).
#
# Item text: not shipped. The file is a spreadsheet with short codes as
#   headers (no variable or value labels at either level). The paper's
#   Table 1 prints the wording of the 30 retained items with their item
#   numbers (= the number in each column code) -- a paper_explicit lead;
#   the 12 items dropped during scale reduction are not printed.
#
# Table (item codes are the source column names):
#   wormley_2017_cteq  42 items  Clinical Teaching Effectiveness
#       Questionnaire, pilot version. Paper: 43 items in four sections --
#       learning experiences (lexp1-12), learning environment (lenv13-19),
#       communication (com20-28), evaluation (eval29-43) -- each rated on a
#       5-point Likert scale from 'strongly disagree' to 'strongly agree'
#       (1-5 asserted). Item 10 is not in the deposit (the paper removed it
#       for a near-zero communality). The "rev" suffix on every column is
#       not explained in the deposit or paper; the responses pile up at 4-5
#       on self-rated teaching behaviours, consistent with 5 = strongly
#       agree. The paper's subscale scores expcreation1, objefficacy1,
#       studentassess1, domainid1 equal the sums of the paper's item sets
#       (asserted); solutionmonitor1 does not equal the sum of items 36-40
#       and is dropped unexamined along with the rest.
#
# Cleaning: 6 respondents answered only lexp1-12 (11 items); they are kept.
#   Three rows (ids 15, 120, 205) answer 5 to all 42 items; 15 and 205 also
#   share gender, age, experience and setting, but differ on other
#   background fields, so neither is dropped as a duplicate.
#
# Dropped: the eight subscale scores (expcreation1, objefficacy1,
#   lenvironment1, feedback1, divcomm1, studentassess1, solutionmonitor1,
#   domainid1); background fields whose codes are not documented anywhere
#   (entryleveldegree, sizegradclass, curricularmodel, highestdgree,
#   certifcation, setting, manager, CCCE, studentsup, APTA, CIBasic,
#   CIAdvance, teachingrole, studentsup2, exp2, tradvother, classsize50).
# id: row index (the file's "ID number" is the same 1..205 sequence).
# Covariates: cov_gender (2 female, 1 male: code 2 is 68.4% of the sample,
#   the paper's female share), cov_age (one age of 0 set to NA),
#   cov_experience (1 = 1-5, 2 = 6-10, 3 = 11+ years as a CI; shares match
#   the paper's 19.1/47.4/33.5%).

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://dataverse.harvard.edu/api/access/datafile/3031544"
       "?format=original")
TABLE = "wormley_2017_cteq"

SECTIONS = {"lexp": [i for i in range(1, 13) if i != 10],
            "lenv": range(13, 20), "com": range(20, 29),
            "eval": range(29, 44)}
ITEMS = [f"{s}{i}rev" for s, r in SECTIONS.items() for i in r]
SUBSCALES = {"expcreation1": [1, 2, 9, 11, 12], "objefficacy1": [3, 4, 5],
             "studentassess1": [29, 30, 35, 41, 43],
             "domainid1": [31, 32, 33]}
COMPOSITES = set(SUBSCALES) | {"lenvironment1", "feedback1", "divcomm1",
                               "solutionmonitor1"}
UNDOCUMENTED = {"entryleveldegree", "sizegradclass", "curricularmodel",
                "highestdgree", "certifcation", "setting", "manager", "CCCE",
                "studentsup", "APTA", "CIBasic", "CIAdvance", "teachingrole",
                "studentsup2", "exp2", "tradvother", "classsize50"}
COVS = {"gender": "cov_gender", "age": "cov_age",
        "experience": "cov_experience"}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (205, 71), d.shape

    # Balance the books.
    assert len(ITEMS) == 42
    known = (set(ITEMS) | COMPOSITES | UNDOCUMENTED | set(COVS)
             | {"ID number"})
    assert set(d.columns) == known, set(d.columns) ^ known
    assert (d["ID number"] == range(1, 206)).all()

    num = {int(re.search(r"\d+", c).group()): c for c in ITEMS}
    for score, ns in SUBSCALES.items():
        cols = [num[n] for n in ns]
        ok = d[cols].notna().all(axis=1) & d[score].notna()
        assert (d.loc[ok, score] == d.loc[ok, cols].sum(axis=1)).all(), score
    assert d["gender"].value_counts(normalize=True).round(3)[2] == 0.684
    assert (d["age"] == 0).sum() == 1
    d["age"] = d["age"].mask(d["age"] == 0)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    allowed = set(range(1, 6))
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - allowed
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 205
    assert long["item"].nunique() == 42
    pv = {i: allowed for i in ITEMS}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
