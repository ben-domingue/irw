#!/usr/bin/env python3
# Source: https://zenodo.org/records/24239172
# DOI: 10.5281/zenodo.24239172 (data)
#   Akhrani LA (2026). Oxford Happiness Questionnaire-Short Form responses from nine Indonesian ethnocultural communities and an urban reference sample [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24239172
# License: CC BY 4.0 (record metadata)
# Data: sheet 'Data Happiness', 1,346 respondents, the file's Subyek. A side table in the sheet gives the scale as
#   '6 likert', items 1, 4, 8 unfavourable, and counts per community (Nagekeo, Sasak, Javanese Solo/Dieng, Tengger, Osing,
#   Badui, Javanese Yogyakarta, Bali) -- but no per-row community code, so none is carried.
# H_7 has two cells coded 7 on the 6-point scale: set missing.
# 419 of 1,346 rows repeat another row's 8-item pattern; most are the consistent patterns a skewed 8-item 6-point
#   scale produces (55555555, 66666666, 25525552 with items 1/4/8 reversed), kept.
# Covariates: none per row. PII: none.
# Item text: codes only; OHQ-SF (Hills & Argyle 2002) Indonesian adaptation not in the deposit.
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
URL = 'https://zenodo.org/api/records/24239172/files/Data%20Happiness%20lintas%20suku.xlsx/content'
N_ROWS = 1346
ID_COL = 'Subyek'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'akhrani_2026_ohq_sf': ['H_1', 'H_2', 'H_3', 'H-4', 'H_5', 'H_6', 'H_7', 'H_8']}
# (lo, hi) response range per table
RANGES = {'akhrani_2026_ohq_sf': (1, 6)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {'akhrani_2026_ohq_sf': [7]}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Total_H': 'sum score',
 'Unnamed: 10': 'side table of sample counts / scale notes, not per-respondent data',
 'Unnamed: 11': 'side table of sample counts / scale notes, not per-respondent data',
 'Unnamed: 12': 'side table of sample counts / scale notes, not per-respondent data',
 'Unnamed: 13': 'side table of sample counts / scale notes, not per-respondent data',
 'Propinsi': 'side table of sample counts / scale notes, not per-respondent data',
 'Suku': 'side table of sample counts / scale notes, not per-respondent data',
 'Unnamed: 16': 'side table of sample counts / scale notes, not per-respondent data',
 'Jumlah': 'side table of sample counts / scale notes, not per-respondent data',
 'Unnamed: 18': 'side table of sample counts / scale notes, not per-respondent data',
 'Unnamed: 19': 'side table of sample counts / scale notes, not per-respondent data'}


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
    covs = list(dict.fromkeys(COVS.values()))
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
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
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
