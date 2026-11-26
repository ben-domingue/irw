#!/usr/bin/env python3
# Source: https://zenodo.org/records/24014378
# DOI: 10.5281/zenodo.24014378 (data)
#   Anonymous (2026). What Do Teachers Know About Intellectual Giftedness? Development and Psychometric Evaluation of the KINGS [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24014378
# License: CC BY 4.0 (record metadata)
# Data: 15_KINGS_Data_Split.csv, 1,667 French teachers, the file's pid; ki01-ki41 on 0-5. cluster is the authors' EFA/CFA split.
#   Depositor anonymous on the record, so the table name uses the instrument acronym.
# Covariates: role, gender, age, education, grade level, tenure, full-time, area type, school type, place, experience, discipline,
#   giftedness training/contact/education, split half, interview time.
# Dropped: consent, departement (geographic), an all-zero missing count.
# PII: none.
# Item text: codes only in the deposit (R script names items by number).
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/24014378/files/15_KINGS_Data_Split.csv/content'
N_ROWS = 1667
ID_COL = 'pid'
COVS = {'job': 'cov_job',
 'gender': 'cov_gender',
 'age': 'cov_age',
 'high_education': 'cov_education',
 'grade': 'cov_grade',
 'titulaire': 'cov_tenured',
 'temps_plein': 'cov_full_time',
 'area': 'cov_area_type',
 'type_school': 'cov_school_type',
 'place': 'cov_place',
 'pro_exp': 'cov_experience_years',
 'discipline': 'cov_discipline',
 'gifted_training': 'cov_gifted_training',
 'gifted_contact': 'cov_gifted_contact',
 'gifted_education': 'cov_gifted_education',
 'cluster': 'cov_split_half',
 'interviewtime': 'cov_completion_time'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'kings_2026_giftedness_knowledge': ['ki01',
                                     'ki02',
                                     'ki03',
                                     'ki04',
                                     'ki05',
                                     'ki06',
                                     'ki07',
                                     'ki08',
                                     'ki09',
                                     'ki10',
                                     'ki11',
                                     'ki12',
                                     'ki13',
                                     'ki14',
                                     'ki15',
                                     'ki16',
                                     'ki17',
                                     'ki18',
                                     'ki19',
                                     'ki20',
                                     'ki21',
                                     'ki22',
                                     'ki23',
                                     'ki24',
                                     'ki25',
                                     'ki26',
                                     'ki27',
                                     'ki28',
                                     'ki29',
                                     'ki30',
                                     'ki31',
                                     'ki32',
                                     'ki33',
                                     'ki34',
                                     'ki35',
                                     'ki36',
                                     'ki37',
                                     'ki38',
                                     'ki39',
                                     'ki40',
                                     'ki41']}
# (lo, hi) response range per table
RANGES = {'kings_2026_giftedness_knowledge': (0, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'consent': 'constant', 'departement': 'French departement code (geographic)', 'missing': 'constant 0'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{})


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
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
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
    covs = list(dict.fromkeys(COVS.values()))
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
