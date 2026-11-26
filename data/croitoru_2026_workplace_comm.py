#!/usr/bin/env python3
# Source: https://zenodo.org/records/23503832
# DOI: 10.5281/zenodo.23503832 (data)
#   Croitoru G, Florea NV, Diaconeasa AA, Stanescu SG (2026). Workplace Communication, Atmosphere, Job Satisfaction and Task Performance: Survey Data from Romanian Employees (N = 286) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23503832
# License: CC BY 4.0 (record metadata)
# Data: Export_SmartPLS.csv, 286 Romanian employees, the deposit's respondent codes R001-R286. README_codebook.txt gives
#   every item's English wording (administered in Romanian) and the scale: 5-point, 1 = strongly disagree .. 5 = strongly agree.
# Tables: one per construct in the codebook (CM, CA, AT, SAT, PERF, 4 items each).
# Covariates: age, gender, position level, tenure (years), education, sector (Romanian labels translated per the codebook).
# PII: none.
# Item text: shipped 2026-11-25c -- the depositors' English from README_codebook.txt (administered in Romanian,
#   fallback); automated_finding/itemtext_verification/make_itemtext_repos_2026-11-25c.py
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
URL = 'https://zenodo.org/api/records/23503832/files/Export_SmartPLS.csv/content'
N_ROWS = 286
ID_COL = 'ID'
COVS = {'Varsta': 'cov_age',
 'Gen': 'cov_gender',
 'Functia': 'cov_position',
 'Vechime_ani': 'cov_tenure_years',
 'Educatie': 'cov_education',
 'Sector': 'cov_sector'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'croitoru_2026_supervisor_comm': ['CM_1', 'CM_2', 'CM_3', 'CM_4'],
 'croitoru_2026_coworker_comm': ['CA_1', 'CA_2', 'CA_3', 'CA_4'],
 'croitoru_2026_work_atmosphere': ['AT_1', 'AT_2', 'AT_3', 'AT_4'],
 'croitoru_2026_job_satisfaction': ['SAT_1', 'SAT_2', 'SAT_3', 'SAT_4'],
 'croitoru_2026_task_performance': ['PERF_1', 'PERF_2', 'PERF_3', 'PERF_4']}
# (lo, hi) response range per table
RANGES = {'croitoru_2026_supervisor_comm': (1, 5),
 'croitoru_2026_coworker_comm': (1, 5),
 'croitoru_2026_work_atmosphere': (1, 5),
 'croitoru_2026_job_satisfaction': (1, 5),
 'croitoru_2026_task_performance': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}
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
    d["Gen"] = d["Gen"].map({"Feminin": "female", "Masculin": "male"})
    d["Functia"] = d["Functia"].map({"Execuție": "execution", "Coordonare": "coordination", "Management": "management"})
    d["Educatie"] = d["Educatie"].map({'Studii medii': 'secondary', 'Studii superioare (licență)': 'bachelor', 'Studii postuniversitare (master/doctorat)': 'postgraduate'})
    d["Sector"] = d["Sector"].map({"Privat": "private", "Public": "public"})
    for c in ["Gen", "Functia", "Educatie", "Sector"]:
        assert d[c].notna().all(), c
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
