#!/usr/bin/env python3
# Source: https://zenodo.org/records/23289746
# DOI: 10.5281/zenodo.23289746 (data)
#   Pham VK (2026). Useful AI Is Not Enough: Trust in AI, Workplace Conditions, and Job Satisfaction [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23289746
# License: CC BY 4.0 (record metadata)
# Data: one sheet, 374 employees; id = row order. The record has no description or codebook: item codes only,
#   every item observed within 1-5 (taken as five-point). PAIU/TAI/JSAT are read from the title (AI usefulness,
#   trust in AI, job satisfaction); PWE, CB, PJS, WA and JR are kept as codes.
# Tables: one per code prefix. Covariates: gender, age band, education, position, work-experience band.
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
URL = 'https://zenodo.org/api/records/23289746/files/HEZ2%202026.08.26%20Data%20(FINAL)%20(8%20constructs).xlsx/content'
N_ROWS = 374
ID_COL = None
COVS = {'Gender': 'cov_gender',
 'Age': 'cov_age_band',
 'Education': 'cov_education',
 'Position': 'cov_position',
 'Work Experience (Years)': 'cov_experience_years_band'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'pham_2026_pwe': ['PWE1', 'PWE2', 'PWE3', 'PWE4', 'PWE5'],
 'pham_2026_cb': ['CB1', 'CB2', 'CB3', 'CB4', 'CB5'],
 'pham_2026_pjs': ['PJS1', 'PJS2', 'PJS3', 'PJS4'],
 'pham_2026_wa': ['WA1', 'WA2', 'WA3', 'WA4', 'WA5'],
 'pham_2026_jr': ['JR1', 'JR2', 'JR3', 'JR4'],
 'pham_2026_ai_usefulness': ['PAIU1', 'PAIU2', 'PAIU3', 'PAIU4'],
 'pham_2026_trust_ai': ['TAI1', 'TAI2', 'TAI3'],
 'pham_2026_job_satisfaction': ['JSAT1', 'JSAT2', 'JSAT3', 'JSAT4', 'JSAT5']}
# (lo, hi) response range per table
RANGES = {'pham_2026_pwe': (1, 5),
 'pham_2026_cb': (1, 5),
 'pham_2026_pjs': (1, 5),
 'pham_2026_wa': (1, 5),
 'pham_2026_jr': (1, 5),
 'pham_2026_ai_usefulness': (1, 5),
 'pham_2026_trust_ai': (1, 5),
 'pham_2026_job_satisfaction': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    for c in ["Gender", "Education", "Position"]:
        d[c] = d[c].map(slug)
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
