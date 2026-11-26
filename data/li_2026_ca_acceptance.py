#!/usr/bin/env python3
# Source: https://zenodo.org/records/22637703
# DOI: 10.5281/zenodo.22637703 (data)
#   Li Q (2026). Social Support and Healthcare CA Dataset [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22637703
# License: CC BY 4.0 (record metadata)
# Data: 'Study 1_survey data.csv', 161 patients, the file's number. Four social-support blocks (INS, CS, ES, IS) and TAM
#   blocks (PEOU, PU, ATT, ITU); codes only, every item observed within 1-7 (seven-point).
# Study 2 (30-adult RCT) is not shipped: below the 100-respondent floor.
# Covariates: none in Study 1. PII: none.
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
URL = 'https://zenodo.org/api/records/22637703/files/Study%201_survey%20data.csv/content'
N_ROWS = 161
ID_COL = 'number'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'li_2026_ca_ins': ['INS1', 'INS2', 'INS3'],
 'li_2026_ca_cs': ['CS1', 'CS2', 'CS3'],
 'li_2026_ca_es': ['ES1', 'ES2', 'ES3', 'ES4'],
 'li_2026_ca_is': ['IS1', 'IS2', 'IS3'],
 'li_2026_ca_peou': ['PEOU1', 'PEOU2', 'PEOU3', 'PEOU4'],
 'li_2026_ca_pu': ['PU1', 'PU2', 'PU3'],
 'li_2026_ca_attitude': ['ATT1', 'ATT2', 'ATT3'],
 'li_2026_ca_intention': ['ITU1', 'ITU2', 'ITU3']}
# (lo, hi) response range per table
RANGES = {'li_2026_ca_ins': (1, 7),
 'li_2026_ca_cs': (1, 7),
 'li_2026_ca_es': (1, 7),
 'li_2026_ca_is': (1, 7),
 'li_2026_ca_peou': (1, 7),
 'li_2026_ca_pu': (1, 7),
 'li_2026_ca_attitude': (1, 7),
 'li_2026_ca_intention': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{})


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d.columns = [c.strip() for c in d.columns]
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
