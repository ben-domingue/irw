#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.34862598.v1
# DOI: 10.6084/m9.figshare.34862598.v1 (data)
#   Gutierrez Angel N (2026). Dataset and Syntax: Structural Model of Emotional Intelligence and Digital Motivation (IMS-DD) [Data set]. figshare. https://doi.org/10.6084/m9.figshare.34862598.v1
# License: CC BY 4.0 (record metadata)
# Data: 'PID(3)(1).sav', 562 Spanish university students, the file's sujeto. TMMS1-24 and MIMD1-10 on 1-5; 13 cells hold
#   6, 33, 35 or 44 (keying slips) and are set missing. One age of 3 is set missing.
# Tables: TMMS-24 and the 10-item digital motivation scale (IMS-DD).
# Covariates: age, sex, degree, course year, social-network use and hours (codes).
# Dropped: the five subscale / scale scores.
# PII: none.
# Item text: no labels in the .sav; the codebook PDF named in the record is not in the deposit.
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
URL = 'https://ndownloader.figshare.com/files/70894674'
N_ROWS = 562
ID_COL = 'sujeto'
COVS = {'edad': 'cov_age',
 'SEXO': 'cov_sex',
 'TITULACION': 'cov_degree',
 'CURSO': 'cov_course_year',
 'REDES': 'cov_social_networks',
 'HORASRED': 'cov_network_hours'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'gutierrezangel_2026_tmms24': ['TMMS1',
                                'TMMS2',
                                'TMMS3',
                                'TMMS4',
                                'TMMS5',
                                'TMMS6',
                                'TMMS7',
                                'TMMS8',
                                'TMMS9',
                                'TMMS10',
                                'TMMS11',
                                'TMMS12',
                                'TMMS13',
                                'TMMS14',
                                'TMMS15',
                                'TMMS16',
                                'TMMS17',
                                'TMMS18',
                                'TMMS19',
                                'TMMS20',
                                'TMMS21',
                                'TMMS22',
                                'TMMS23',
                                'TMMS24'],
 'gutierrezangel_2026_mimd': ['MIMD1',
                              'MIMD2',
                              'MIMD3',
                              'MIMD4',
                              'MIMD5',
                              'MIMD6',
                              'MIMD7',
                              'MIMD8',
                              'MIMD9',
                              'MIMD10']}
# (lo, hi) response range per table
RANGES = {'gutierrezangel_2026_tmms24': (1, 5), 'gutierrezangel_2026_mimd': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {'gutierrezangel_2026_tmms24': [6, 33], 'gutierrezangel_2026_mimd': [33, 35, 44, 6]}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'AE': 'subscale / scale score',
 'CE': 'subscale / scale score',
 'RE': 'subscale / scale score',
 'MI': 'subscale / scale score',
 'MT': 'subscale / scale score'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    import pyreadstat, tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(content); f.flush()
        d, _ = pyreadstat.read_sav(f.name, user_missing=False)
    return d


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d.loc[d["edad"] < 15, "edad"] = np.nan   # one age of 3 in a university sample
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
