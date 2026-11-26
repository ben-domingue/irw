#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.34920888.v1
# DOI: 10.6084/m9.figshare.34920888.v1 (data)
#   Wang N (2026). From Collegiate Sport Experiences to Exercise Adherence: Investigating the Mediating Roles of Exercise Nostalgia and Self-Efficacy [Data set]. figshare. https://doi.org/10.6084/m9.figshare.34920888.v1
# License: CC BY 4.0 (record metadata)
# Data: analysis_data_.csv, 345 young adults (19-27); id = row order. The record gives the block sizes: collegiate sport
#   experiences 14, exercise nostalgia 33 (LE 5 + EN 7 + SO 6 + PI 7 + GI 8), general self-efficacy 10, exercise adherence 12
#   (PF/EF/RF x 4). Ranges as observed (1-7, 1-7, 1-4, 1-5).
# Tables: the four instruments, sub-dimension codes kept in the item names.
# Covariates: sex (code), age.
# Dropped: four CS composite means.
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
URL = 'https://ndownloader.figshare.com/files/71107941'
N_ROWS = 345
ID_COL = None
COVS = {'SEX': 'cov_sex', 'AGE': 'cov_age'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'wang_2026_collegiate_sport_exp': ['CS1',
                                    'CS2',
                                    'CS3',
                                    'CS4',
                                    'CS5',
                                    'CS6',
                                    'CS7',
                                    'CS8',
                                    'CS9',
                                    'CS10',
                                    'CS11',
                                    'CS12',
                                    'CS13',
                                    'CS14'],
 'wang_2026_exercise_nostalgia': ['LE1',
                                  'LE2',
                                  'LE3',
                                  'LE4',
                                  'LE5',
                                  'EN1',
                                  'EN2',
                                  'EN3',
                                  'EN4',
                                  'EN5',
                                  'EN6',
                                  'EN7',
                                  'SO1',
                                  'SO2',
                                  'SO3',
                                  'SO4',
                                  'SO5',
                                  'SO6',
                                  'PI1',
                                  'PI2',
                                  'PI3',
                                  'PI4',
                                  'PI5',
                                  'PI6',
                                  'PI7',
                                  'GI1',
                                  'GI2',
                                  'GI3',
                                  'GI4',
                                  'GI5',
                                  'GI6',
                                  'GI7',
                                  'GI8'],
 'wang_2026_gses': ['SE1', 'SE2', 'SE3', 'SE4', 'SE5', 'SE6', 'SE7', 'SE8', 'SE9', 'SE10'],
 'wang_2026_exercise_adherence': ['PF1', 'PF2', 'PF3', 'PF4', 'EF1', 'EF2', 'EF3', 'EF4', 'RF1', 'RF2', 'RF3', 'RF4']}
# (lo, hi) response range per table
RANGES = {'wang_2026_collegiate_sport_exp': (1, 7),
 'wang_2026_exercise_nostalgia': (1, 7),
 'wang_2026_gses': (1, 4),
 'wang_2026_exercise_adherence': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'CS_CLASS_MEAN': 'composite mean',
 'CS_FACILITY_MEAN': 'composite mean',
 'CS_VARSITY_MEAN': 'composite mean',
 'CS_CLUB_MEAN': 'composite mean'}
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
