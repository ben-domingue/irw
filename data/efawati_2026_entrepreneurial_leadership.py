#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/DHFHMV
# DOI: 10.7910/DVN/DHFHMV (data)
#   Efawati Y, Chaniago H, Andriani R, Veranita M (2026). Entrepreneurial Leadership and Work Performance: When Creativity Becomes the Key [Data set]. Dataverse. https://doi.org/10.7910/DVN/DHFHMV
# License: CC0 1.0 (record metadata)
# Data: 'Supplementary Data 1 - Database and Codebook.xlsx', sheet 'data penelitian' (header on row 3), 184 Indonesian
#   employees; id = row order. The codebook sheet gives every item's English wording; every item observed within 1-5.
# Tables: one per construct.
# Covariates: gender, age, education, experience as numeric codes -- the codebook's category lists do not match the
#   stored codes (gender stored 0-2 for two categories; age 1-3 for four bands), so the codes are carried as they are.
# Dropped: the three sums.
# PII: none.
# Item text: English wording for all 29 items in the xlsx 'codebook' sheet; questionnaire PDF in the deposit (cheap later build).
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/14244436'
N_ROWS = 184
ID_COL = None
COVS = {'Gender': 'cov_gender', 'Age': 'cov_age_band', 'Education': 'cov_education', 'Experience': 'cov_experience_band'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'efawati_2026_entrepreneurial_leadership': ['EL1', 'EL2', 'EL3', 'EL4', 'EL5', 'EL6', 'EL7', 'EL8', 'EL9', 'EL10'],
 'efawati_2026_individual_creativity': ['IC1', 'IC2', 'IC3', 'IC4', 'IC5', 'IC6', 'IC7', 'IC8', 'IC9'],
 'efawati_2026_work_performance': ['WP1', 'WP2', 'WP3', 'WP4', 'WP5', 'WP6', 'WP7', 'WP8', 'WP9', 'WP10']}
# (lo, hi) response range per table
RANGES = {'efawati_2026_entrepreneurial_leadership': (1, 5),
 'efawati_2026_individual_creativity': (1, 5),
 'efawati_2026_work_performance': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Sum_EL': 'sum score', 'Sum_IC': 'sum score', 'Sum_WP': 'sum score'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=2)


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
