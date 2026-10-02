#!/usr/bin/env python3
# Source: https://zenodo.org/records/2643228
# DOI: 10.1007/s00508-020-01670-5
#   Fazekas, Avian, Noehrer, Matzer, Vajda, Hannich & Neubauer (2020).
#   "Interoceptive awareness and self-regulation contribute to psychosomatic
#   competence as measured by a new inventory." Wiener klinische
#   Wochenschrift 134, 581-592. (PMC9418284, CC BY.)
# Data: Zenodo 10.5281/zenodo.2643228 (Fazekas, 2019),
#       "PSCI_fazekas_data_4_archive.sav" (103 rows x 94 columns). This is the
#       paper's field test: 103 Austrian adults (Graz) answering the 65 items
#       that survived the pre-test, in German.
# License: CC BY 4.0 (Zenodo record metadata, zenodo.org/api/records/2643228).
#
# Item text: not shipped. Both label levels checked: item01-item65 carry no
#   variable labels and no value labels (only the demographics and the
#   criterion totals are labelled). The paper's Table 3 prints the English
#   wording of the 44 FINAL items under their own codes (IA-1, M-1, ...), but
#   nothing in the deposit or the paper maps item01-item65 onto those codes,
#   so the text is a reconstruction away, not one hop.
#
# Tables:
#   fazekas_2019_psci   65 items, 1-6  Psychosomatic Competence Inventory,
#                        field-test version. 6-point Likert (strongly disagree,
#                        disagree, somewhat disagree, somewhat agree, agree,
#                        strongly agree) per the paper's Methods. The final
#                        PSCI keeps 44 of these 65 items in six scales; all 65
#                        are shipped because all 65 were administered. Item
#                        codes are the source column names. Responses are as
#                        deposited; the paper does not say whether any item was
#                        reversed before archiving.
#   The triage record's old QC failure (resp_scale_mixed) was only that some
#   items were never answered 1 (observed 2-6); that is a warning now, and the
#   documented 1-6 set is passed to run_qc below.
#
# Dropped as items:
#   - F1-F6_sumscore and F1-F6_IRT_score: the authors' scale scores.
#   - SAM_P, SAM_OE, APM, d2, SR, SWE, Sport, B_L: totals of the validation
#     measures (self-consciousness, Raven APM, d2 attention, self-regulation,
#     self-efficacy, physical activity, bodily complaints). Totals only, no
#     item data; missing for 46-48 respondents.
#   - BMI (continuous; not carried).
#
# id: row index. The source `Code` column is a study pseudonym (e.g.
#   'M0689GG'); it is dropped rather than carried. No names, emails, birth
#   dates, IP or GPS anywhere in the file.
# Covariates: cov_age, cov_sex (1 male, 2 female), cov_smoker (1 smoker,
#   0 non-smoker; the file's value labels say 1/2 but the data are 0/1, and
#   19 ones matches the paper's 19 smokers), cov_marital (1 unmarried,
#   2 married, 3 divorced, 4 widowed), cov_living (1 alone, 2 with partner
#   and/or children, 3 shared flat, 4 with parents/relatives), cov_education
#   (1-4, ISCED-style labels in the .sav), cov_employed (1 employed,
#   2 not employed).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/2643228/files/"
       "PSCI_fazekas_data_4_archive.sav/content")

TABLE = "fazekas_2019_psci"
ITEMS = [f"item{i:02d}" for i in range(1, 66)]
ALLOWED = range(1, 7)

COVS = {"Age": "cov_age", "sex": "cov_sex", "smoking": "cov_smoker",
        "Marital_status": "cov_marital", "Living_situation": "cov_living",
        "Highest_educational": "cov_education",
        "Employment_status": "cov_employed"}
DROPPED = (["Code", "BMI", "SAM_P", "SAM_OE", "APM", "d2", "SR", "SWE",
            "Sport", "B_L"]
           + [f"F{i}_sumscore" for i in range(1, 7)]
           + [f"F{i}_IRT_score" for i in range(1, 7)])


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, _ = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (103, 94), d.shape

    # Balance the books: every column is an item, a covariate, or named.
    rest = set(d.columns) - set(ITEMS) - set(COVS) - set(DROPPED)
    assert rest == set(), rest
    assert set(d["smoking"].dropna()) == {0, 1} and d["smoking"].sum() == 19

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - set(ALLOWED)
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(ITEMS)

    pv = {i: set(ALLOWED) for i in ITEMS}
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
