#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.35092204.v1
# DOI: 10.6084/m9.figshare.35092204.v1 (data)
#   Pretorius T (2026). Trauma exposure, meaning in life and PTSD [Data set]. figshare. https://doi.org/10.6084/m9.figshare.35092204.v1
# License: CC BY 4.0 (record metadata)
# Data: one sheet, 450 South African university students; id = row order. LEC items are the authors' weighted exposure codes (0-3),
#   MLQ 1-7 with item 9 already reversed (MLQ9_R; the MLQ's one reverse-keyed item, so the reversal is verifiable), SPRINT 0-4.
# Covariates: age, gender, student level, urban/rural home, accessed psychological services.
# Dropped: four totals.
# PII: none.
# Item text: codes only; LEC-5, MLQ (Steger et al. 2006) and SPRINT are published instruments.
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
URL = 'https://ndownloader.figshare.com/files/71788324'
N_ROWS = 450
ID_COL = None
COVS = {'age': 'cov_age',
 'gender': 'cov_gender',
 'student': 'cov_student_level',
 'home': 'cov_home',
 'accesed psych_services': 'cov_psych_services'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'pretorius_2026_lec_weighted': ['lec1_Weighted',
                                 'lec2_Weighted',
                                 'lec3_Weighted',
                                 'lec4_Weighted',
                                 'lec5_Weighted',
                                 'lec6_Weighted',
                                 'lec7_Weighted',
                                 'lec8_Weighted',
                                 'lec9_Weighted',
                                 'lec10_Weighted',
                                 'lec11_Weighted',
                                 'lec12_Weighted',
                                 'lec13_Weighted',
                                 'lec14_Weighted',
                                 'lec15_Weighted',
                                 'lec16_Weighted',
                                 'lec17_Weighted'],
 'pretorius_2026_mlq': ['MLQ1', 'MLQ2', 'MLQ3', 'MLQ4', 'MLQ5', 'MLQ6', 'MLQ7', 'MLQ8', 'MLQ9_R', 'MLQ10'],
 'pretorius_2026_sprint8': ['sprint1', 'sprint2', 'sprint3', 'sprint4', 'sprint5', 'sprint6', 'sprint7', 'sprint8']}
# (lo, hi) response range per table
RANGES = {'pretorius_2026_lec_weighted': (0, 3), 'pretorius_2026_mlq': (1, 7), 'pretorius_2026_sprint8': (0, 4)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Trauma Exposure': 'scale total', 'Presence': 'scale total', 'Search': 'scale total', 'PTSD': 'scale total'}
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
    for c in ["gender", "student", "home", "accesed psych_services"]:
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
