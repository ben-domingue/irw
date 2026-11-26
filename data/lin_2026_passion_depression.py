#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.35098999.v1
# DOI: 10.6084/m9.figshare.35098999.v1 (data)
#   Lin P (2026). The impact of harmonious passion on depression among university students: The mediating role of sports participation and the moderating effect of flow trait [Data set]. figshare. https://doi.org/10.6084/m9.figshare.35098999.v1
# License: CC BY 4.0 (record metadata)
# Data: data.sav (no variable or value labels), 778 university students in Shandong, China; id = row order. Blocks are
#   read from the record's model: X = harmonious passion (predictor), M = sports participation (mediator), W = flow trait
#   (moderator), Y = depression (outcome). The 36-item W, 6-item X and 21-item Y match common instruments in size and
#   range, but the deposit does not name them.
# The record lists data.sav twice (identical size); the first copy is read.
# Tables: one per block.
# Covariates: gender, age, grade (codes as stored).
# Dropped: X, M, W, WW, Y scores.
# PII: none.
# Item text: no labels in the .sav; instruments not named in the deposit.
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
URL = 'https://ndownloader.figshare.com/files/71808808'
N_ROWS = 778
ID_COL = None
COVS = {'Gender': 'cov_gender', 'Age': 'cov_age', 'Grade': 'cov_grade'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'lin_2026_harmonious_passion': ['X1', 'X2', 'X3', 'X4', 'X5', 'X6'],
 'lin_2026_sport_participation': ['M1', 'M2', 'M3'],
 'lin_2026_flow_trait': ['W1',
                         'W2',
                         'W3',
                         'W4',
                         'W5',
                         'W6',
                         'W7',
                         'W8',
                         'W9',
                         'W10',
                         'W11',
                         'W12',
                         'W13',
                         'W14',
                         'W15',
                         'W16',
                         'W17',
                         'W18',
                         'W19',
                         'W20',
                         'W21',
                         'W22',
                         'W23',
                         'W24',
                         'W25',
                         'W26',
                         'W27',
                         'W28',
                         'W29',
                         'W30',
                         'W31',
                         'W32',
                         'W33',
                         'W34',
                         'W35',
                         'W36'],
 'lin_2026_depression': ['Y1',
                         'Y2',
                         'Y3',
                         'Y4',
                         'Y5',
                         'Y6',
                         'Y7',
                         'Y8',
                         'Y9',
                         'Y10',
                         'Y11',
                         'Y12',
                         'Y13',
                         'Y14',
                         'Y15',
                         'Y16',
                         'Y17',
                         'Y18',
                         'Y19',
                         'Y20',
                         'Y21']}
# (lo, hi) response range per table
RANGES = {'lin_2026_harmonious_passion': (1, 7),
 'lin_2026_sport_participation': (1, 5),
 'lin_2026_flow_trait': (1, 5),
 'lin_2026_depression': (0, 3)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'X': 'mean score', 'M': 'PARS-3 score', 'W': 'mean score', 'WW': 'mean score', 'Y': 'sum score'}
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
