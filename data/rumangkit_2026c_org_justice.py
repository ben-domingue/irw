#!/usr/bin/env python3
# Source: https://zenodo.org/records/24267383
# DOI: 10.5281/zenodo.24267383 (data)
#   Rumangkit S (2026). Dataset Questionnaire Organizational Justice and Job Performance [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24267383
# License: CC BY 4.0 (record metadata)
# Data: 'Dataset_OJ and Performance.xlsx', 272 Indonesian employees; id = row order. Code-prefix blocks on 1-5; KY8/KY10 appear as KU8/KU10
#   inside the KY run and are kept with it (item = the stored code).
# Not the same respondents as rumangkit_2026_* / rumangkit_2026b_* (zenodo 21522509 / 22089166, 100 employees each): none of the 272
#   17-item OCB patterns here occurs in 21522509; hence the 2026c suffix.
# Covariates: none in the deposit.
# PII: none.
# Item text: codes only in the deposit.
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
URL = 'https://zenodo.org/api/records/24267383/files/Dataset_OJ%20and%20Performance.xlsx/content'
N_ROWS = 272
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'rumangkit_2026c_org_justice': ['KO1',
                                 'KO2',
                                 'KO3',
                                 'KO4',
                                 'KO5',
                                 'KO6',
                                 'KO7',
                                 'KO8',
                                 'KO9',
                                 'KO10',
                                 'KO11',
                                 'KO12',
                                 'KO13',
                                 'KO14',
                                 'KO15',
                                 'KO16',
                                 'KO17'],
 'rumangkit_2026c_ocb': ['OCB1',
                         'OCB2',
                         'OCB3',
                         'OCB4',
                         'OCB5',
                         'OCB6',
                         'OCB7',
                         'OCB8',
                         'OCB9',
                         'OCB10',
                         'OCB11',
                         'OCB12',
                         'OCB13',
                         'OCB14',
                         'OCB15',
                         'OCB16',
                         'OCB17'],
 'rumangkit_2026c_kk': ['KK1', 'KK2', 'KK3', 'KK4', 'KK5', 'KK6', 'KK7'],
 'rumangkit_2026c_job_performance': ['KY1', 'KY2', 'KY3', 'KY4', 'KY5', 'KY6', 'KY7', 'KU8', 'KY9', 'KU10', 'KY11'],
 'rumangkit_2026c_eh': ['EH1', 'EH2', 'EH 3']}
# (lo, hi) response range per table
RANGES = {'rumangkit_2026c_org_justice': (1, 5),
 'rumangkit_2026c_ocb': (1, 5),
 'rumangkit_2026c_kk': (1, 5),
 'rumangkit_2026c_job_performance': (1, 5),
 'rumangkit_2026c_eh': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


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
