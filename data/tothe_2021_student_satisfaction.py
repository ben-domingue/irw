#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/7cjz65mg6g
# DOI: 10.17632/7cjz65mg6g (data)
#   To-The N, Khuc-Van Q, Hoang-Duc C, et al. (2021). Dataset on factors influencing Vietnamese student's motivation and
#   satisfaction under COVID-19 context [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: educational-factors.xlsx, sheet "data": 1,680 Vietnamese university students (online survey), the deposit's own
#   No. column. The "details" sheet gives every question group, every item's wording and the scale (5-point, 1 = Bad,
#   5 = Good) and the demographic codes.
# Tables, one per question group in the details sheet, item = the deposit's code: _lecturer_quality (a13_1-6),
#   _program_quality (a14_1-6), _facilities (a15_1-6), _extracurricular (a16_1-6), _social_factors (a17_1-5),
#   _family_friends (a18_1-7), _personal_factors (a19_1-6), _study_motivation (a20_1-5), _study_satisfaction
#   (a21_1-9), _online_learning (b1_1-3), _covid_satisfaction (b2_1-4, last-year satisfaction with air, noise,
#   transport, food hygiene), _overall_satisfaction (b3_1-4, same four domains overall), _other_satisfaction (b4_1-8).
# Covariates: cov_major (a2), cov_gender (a3), cov_father_occupation (a6), decoded from the details sheet.
# PII: none (all columns numeric).
# Item text: not shipped -- stems for every item are in the "details" sheet with the endpoint anchors (1 = Bad,
#   5 = Good); a cheap build later. The questionnaire appears author-developed (no source cited).
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://data.mendeley.com/public-files/datasets/7cjz65mg6g/files/b04367ee-7578-4c93-97f4-7abb479022ca/file_downloaded'
N_ROWS = 1680
ID_COL = 'No.'
COVS = {'a2': 'cov_major', 'a3': 'cov_gender', 'a6': 'cov_father_occupation'}
COV_MAPS = {'cov_major': {1: 'natural_sciences', 2: 'social_sciences'},
 'cov_gender': {1: 'male', 2: 'female'},
 'cov_father_occupation': {1: 'farmer',
                           2: 'doctor',
                           3: 'entrepreneur',
                           4: 'retired',
                           5: 'state_official',
                           6: 'soldier',
                           7: 'merchandiser',
                           8: 'freelancer',
                           9: 'teacher',
                           10: 'physical_worker',
                           11: 'craftsman',
                           12: 'enterprise_employee',
                           13: 'constructor',
                           14: 'unemployed',
                           15: 'deceased',
                           16: 'foreign_settler'}}
RENAME = {}
BLOCKS = {'tothe_2021_lecturer_quality': ['a13_1', 'a13_2', 'a13_3', 'a13_4', 'a13_5', 'a13_6'],
 'tothe_2021_program_quality': ['a14_1', 'a14_2', 'a14_3', 'a14_4', 'a14_5', 'a14_6'],
 'tothe_2021_facilities': ['a15_1', 'a15_2', 'a15_3', 'a15_4', 'a15_5', 'a15_6'],
 'tothe_2021_extracurricular': ['a16_1', 'a16_2', 'a16_3', 'a16_4', 'a16_5', 'a16_6'],
 'tothe_2021_social_factors': ['a17_1', 'a17_2', 'a17_3', 'a17_4', 'a17_5'],
 'tothe_2021_family_friends': ['a18_1', 'a18_2', 'a18_3', 'a18_4', 'a18_5', 'a18_6', 'a18_7'],
 'tothe_2021_personal_factors': ['a19_1', 'a19_2', 'a19_3', 'a19_4', 'a19_5', 'a19_6'],
 'tothe_2021_study_motivation': ['a20_1', 'a20_2', 'a20_3', 'a20_4', 'a20_5'],
 'tothe_2021_study_satisfaction': ['a21_1', 'a21_2', 'a21_3', 'a21_4', 'a21_5', 'a21_6', 'a21_7', 'a21_8', 'a21_9'],
 'tothe_2021_online_learning': ['b1_1', 'b1_2', 'b1_3'],
 'tothe_2021_covid_satisfaction': ['b2_1', 'b2_2', 'b2_3', 'b2_4'],
 'tothe_2021_overall_satisfaction': ['b3_1', 'b3_2', 'b3_3', 'b3_4'],
 'tothe_2021_other_satisfaction': ['b4_1', 'b4_2', 'b4_3', 'b4_4', 'b4_5', 'b4_6', 'b4_7', 'b4_8']}
# (lo, hi) response range per table
RANGES = {'tothe_2021_lecturer_quality': (1, 5),
 'tothe_2021_program_quality': (1, 5),
 'tothe_2021_facilities': (1, 5),
 'tothe_2021_extracurricular': (1, 5),
 'tothe_2021_social_factors': (1, 5),
 'tothe_2021_family_friends': (1, 5),
 'tothe_2021_personal_factors': (1, 5),
 'tothe_2021_study_motivation': (1, 5),
 'tothe_2021_study_satisfaction': (1, 5),
 'tothe_2021_online_learning': (1, 5),
 'tothe_2021_covid_satisfaction': (1, 5),
 'tothe_2021_overall_satisfaction': (1, 5),
 'tothe_2021_other_satisfaction': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name="data")


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == N_ROWS, len(d)
    d = d.rename(columns=RENAME)
    d = prep(d)
    if ID_COL:
        assert d[ID_COL].is_unique, "duplicate ids"
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        if cov in COV_MAPS:
            d[src] = d[src].map(lambda v: v.strip() if isinstance(v, str) else v)
            d[cov] = d[src].map(COV_MAPS[cov])
            assert d[cov].notna().sum() == d[src].notna().sum(), (cov, set(d[src].dropna()) - set(COV_MAPS[cov]))
        else:
            d[cov] = d[src]
    covs = list(COVS.values())
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
