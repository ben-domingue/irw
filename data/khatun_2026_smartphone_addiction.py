#!/usr/bin/env python3
# Source: https://zenodo.org/records/19685114
# DOI: 10.1371/journal.pone.0353865
#   Khatun, S., Ridoy, M. M. H., Noman, A. H., Sharon, M. M. H., Mia, M. R.,
#   Islam, J., Himel, S. H., & Shahrier, M. A. (2026). "Bangla validation of
#   the smartphone addiction scale and the academic underachievement scale:
#   The associative role of classroom mindful attention in the relationship
#   between smartphone addiction and underachievement among adolescents and
#   young adults." PLOS One. (The paper's Data Availability statement points
#   at this Zenodo record.)
# Data: Zenodo 19685114, "SA,CMARS, and PAUS Manuscript Combined Data
#       FINAL.sav" (712 rows x 49 columns; Bangladeshi adolescents and young
#       adults, online and offline administration). The deposit's two other
#       .sav files are the adolescent (178) and young-adult (534) subsets of
#       this one: their union is row-for-row the combined file (asserted on
#       the full row multiset when this script was written), so only the
#       combined file is read.
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. Both label levels checked: no variable labels on
#   any item (only the three totals carry one); value labels on every item
#   carry the English response anchors only. The Bangla stems are not in the
#   deposit; the instruments are SAS-SV (Kwon et al. 2013), PAUS and CMARS
#   in their published sources.
#
# Tables (item codes are the source column names). Scale identities and
# response ranges are from the paper's Measures section:
#   khatun_2026_sas    SAS_1-SAS_10  Smartphone Addiction Scale - Short
#                      Version, 6-point (1 strongly disagree .. 6 strongly
#                      agree).
#   khatun_2026_paus   PAUS_1-PAUS_6  Perceived Academic Underachievement
#                      Scale, 5-point (1 strongly disagree .. 5 strongly
#                      agree). The paper reverse-codes item 2; PAUS_2
#                      correlates positively (r >= .5) with every other item,
#                      so the file holds it AFTER that recode.
#   khatun_2026_cmars  CMARS_1_SA .. CMARS_10_ER  Classroom Mindful Attention
#                      Regulation Scale, 5-point (1 almost never .. 5 almost
#                      always); suffix SA = self-awareness, ER = emotional
#                      regulation. The paper reverse-scores the negatively
#                      worded items 2, 4, 5, 8, 10. The file's value labels
#                      run "Almost Always .. Almost never" on the *_SA items
#                      and "Almost never .. Almost always" on the *_ER items,
#                      and every inter-item correlation is positive, so the
#                      stored codes share one keying; which items carry the
#                      reversal is not stated by the deposit.
#
# Cleaning:
#   - CMARS_1_SA holds 0 for 102 respondents. 0 is neither a value label nor
#     a point on the paper's 1-5 scale -> NA. (The deposit's CMARS_T total
#     includes those zeros as zero.)
#   - Covariates: Physical_problem has one 5 and
#     Mental_disorder_last_6_months one 7, both outside their yes/no labels
#     -> NA.
#
# Dropped: SAS_T, PAUS_T, CMARS_T, CMARS_SA, CMARS_ER (sums of the items,
#   asserted).
# id: row index (the file has no respondent id).
# Covariates: cov_data_mode (1 online, 2 offline), cov_sample (Age_limit:
#   1 adolescent file "12 to 18", 2 young-adult file "19 to 24"; the
#   observed ages are 15-20 and 18-27, so the label is the sample, not the
#   age), cov_age, cov_gender (1 female, 2 male), cov_marital (1 married,
#   2 unmarried), cov_permanent_residence (1 urban, 2 rural),
#   cov_present_residence (1 hall, 2 mess, 3 house, 4 other), cov_education
#   (1 secondary .. 4 MS), cov_faculty (1 science, 2 non-science),
#   cov_achievement (1 high, 2 medium, 3 low), cov_gpa, cov_ses (1 lower ..
#   5 upper class), cov_family_income (monthly, BDT),
#   cov_academic_hours (time spent on academic tasks), cov_physical_problem
#   (1 yes, 2 no), cov_mental_disorder_6m (1 yes, 2 no), cov_sleep_hours,
#   cov_smoking (1 yes, 2 no).

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
URL = ("https://zenodo.org/api/records/19685114/files/"
       "SA,CMARS,%20and%20PAUS%20Manuscript%20Combined%20Data%20FINAL.sav/"
       "content")

CMARS = ["CMARS_1_SA", "CMARS_2_ER", "CMARS_3_SA", "CMARS_4_ER",
         "CMARS_5_ER", "CMARS_6_SA", "CMARS_7_SA", "CMARS_8_ER",
         "CMARS_9_SA", "CMARS_10_ER"]
TABLES = {
    "khatun_2026_sas": ([f"SAS_{i}" for i in range(1, 11)], range(1, 7)),
    "khatun_2026_paus": ([f"PAUS_{i}" for i in range(1, 7)], range(1, 6)),
    "khatun_2026_cmars": (CMARS, range(1, 6)),
}
COMPOSITES = {"SAS_T": "khatun_2026_sas", "PAUS_T": "khatun_2026_paus",
              "CMARS_T": "khatun_2026_cmars"}
SUBSCALES = {"CMARS_SA": [c for c in CMARS if c.endswith("_SA")],
             "CMARS_ER": [c for c in CMARS if c.endswith("_ER")]}
COVS = {"Data_Mode": "cov_data_mode", "Age_limit": "cov_sample",
        "Age_of_student": "cov_age", "Gender": "cov_gender",
        "Marital_status": "cov_marital",
        "Permanent_resident": "cov_permanent_residence",
        "Present_resident": "cov_present_residence",
        "Education": "cov_education", "Faculty": "cov_faculty",
        "Academic_Achievement": "cov_achievement", "GPA_CGPA": "cov_gpa",
        "Socio_economic_condition": "cov_ses",
        "Family_income_monthly": "cov_family_income",
        "Time_spend_academic_tasks": "cov_academic_hours",
        "Physical_problem": "cov_physical_problem",
        "Mental_disorder_last_6_months": "cov_mental_disorder_6m",
        "Sleeping_hours": "cov_sleep_hours", "Smoking": "cov_smoking"}
FLOAT_COVS = {"cov_gpa"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (712, 49), d.shape

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | set(COMPOSITES) | set(SUBSCALES) | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known

    for tot, table in COMPOSITES.items():
        assert (d[TABLES[table][0]].sum(axis=1) == d[tot]).all(), tot
    for sub, its in SUBSCALES.items():
        assert (d[its].sum(axis=1) == d[sub]).all(), sub

    # Out-of-label codes -> NA.
    assert (d["CMARS_1_SA"] == 0).sum() == 102
    d.loc[d["CMARS_1_SA"] == 0, "CMARS_1_SA"] = pd.NA
    assert (d["Physical_problem"] == 5).sum() == 1
    d.loc[d["Physical_problem"] == 5, "Physical_problem"] = pd.NA
    assert (d["Mental_disorder_last_6_months"] == 7).sum() == 1
    d.loc[d["Mental_disorder_last_6_months"] == 7,
          "Mental_disorder_last_6_months"] = pd.NA

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, scale) in TABLES.items():
        allowed = set(scale)
        for c in its:
            labs = set(meta.variable_value_labels[c])
            assert labs == {float(v) for v in allowed}, (c, labs)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            if c not in FLOAT_COVS:
                long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(
            str(out), profile="upload", context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
