#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/34966957 (dataset, bilingual questionnaires and codebook); the
#   same .sav is also deposited alone as figshare record "SPSS Dataset for Development and initial validation of
#   HEALTHPERF ..." and is built once, from this record.
# DOI: figshare 34966957 (data)
#   Endeshaw B (2026). Dataset, Bilingual Questionnaires, and Codebook for: Development and initial validation of
#   HEALTHPERF: a framework for measuring healthcare service quality in three public hospitals in Ethiopia
#   [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: "S1_SPSS Dataset Anonymized dataset for EFA and CFA..sav", 961 respondents (patients and attendants, managers,
#   clinicians and support staff) at three Addis Ababa public hospitals. S2_Codebook.pdf gives every item's wording
#   and dimension and the scale, 1 = Very strongly disagree .. 7 = Very strongly agree (the .sav value labels agree).
#   60 items; the code's first digit is the dimension: tangibles (q11-q112), technical qualities (q21-q28), personal
#   care (q31-q315), assurance (q41-q49), medical administration (q51-...), reliability (q61-...).
# Table: endeshaw_2026_healthperf -- one table for the instrument (item = the .sav variable name). id = the file's ID.
# Covariates (from the .sav value labels): cov_hospital, cov_gender, cov_age (years), cov_respondent_group. The three
#   duration columns (stay or employment, up to 10,080) and the analysis flags (missing, SD, valid_sample,
#   sample_split, filter_$) are not carried.
# Item text: not shipped -- S2_Codebook.pdf has every English stem by code and the anchors, and the record has the
#   English and Amharic questionnaire; a cheap build later (author-developed instrument).
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://ndownloader.figshare.com/files/71293720'
N_ROWS = 961
ID_COL = 'ID'
COVS = {'NameHospital': 'cov_hospital', 'Gender': 'cov_gender', 'Age': 'cov_age', 'RespoGroup': 'cov_respondent_group'}
COV_MAPS = {'cov_hospital': {1.0: 'tikur_anbessa', 2.0: 'st_paul', 3.0: 'alert'}, 'cov_gender': {1.0: 'female', 2.0: 'male'}, 'cov_respondent_group': {1.0: 'inpatient_or_family', 2.0: 'outpatient_or_family', 3.0: 'manager', 4.0: 'pharmacy_lab_radiology', 5.0: 'physician', 6.0: 'nurse_health_officer', 7.0: 'support_staff'}}
RENAME = {}
BLOCKS = {'endeshaw_2026_healthperf': ['q11', 'q12', 'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q110', 'q111', 'q112', 'q21', 'q22', 'q23', 'q24', 'q25', 'q26', 'q27', 'q28', 'q31', 'q32', 'q33', 'q34', 'q35', 'q36', 'q37', 'q38', 'q39', 'q310', 'q311', 'q312', 'q313', 'q314', 'q315', 'q41', 'q42', 'q43', 'q44', 'q45', 'q46', 'q47', 'q48', 'q49', 'q51', 'q52', 'q53', 'q54', 'q55', 'q56', 'q57', 'q58', 'q59', 'q510', 'q61', 'q62', 'q63', 'q64', 'q65', 'q66']}
LO, HI = 1, 7
DROP_COLS = []


def load(content):
    import os, tempfile
    import pyreadstat
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(content)
    try:
        d, meta = pyreadstat.read_sav(f.name)
    finally:
        os.unlink(f.name)
    assert meta.variable_value_labels["q11"][1.0] == "Very strongly disagree" and meta.variable_value_labels["q11"][7.0] == "Very strongly agree"
    return d


def keep_rows(d):
    return d


def main():
    r = requests.get(URL, timeout=180, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    assert len(d) == N_ROWS, len(d)
    d = d.drop(columns=[c for c in DROP_COLS if c in d.columns])
    d = keep_rows(d)
    if ID_COL:
        assert d[ID_COL].is_unique
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        d[cov] = d[src].map(COV_MAPS[cov]) if cov in COV_MAPS else d[src]
        if cov in COV_MAPS:
            assert d[cov].notna().sum() == d[src].notna().sum(), cov
    covs = list(COVS.values())
    shipped = set()
    for name, items in BLOCKS.items():
        assert all(c in d for c in items), [c for c in items if c not in d]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(LO, HI).all() and (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(LO, HI + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert name not in shipped
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    used = set(sum(BLOCKS.values(), [])) | set(COVS) | {ID_COL}
    print("source columns not shipped:", [c for c in d.columns if c not in used and c != "id" and c not in covs])


if __name__ == "__main__":
    main()
