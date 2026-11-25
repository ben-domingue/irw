#!/usr/bin/env python3
# Source: https://zenodo.org/records/24240975
# DOI: 10.5281/zenodo.24240975 (data)
#   Akhrani LA (2026). Fighting for joy: Self-esteem and gratitude as predictors of happiness among participants of the Etu ritual boxing tradition [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24240975
# License: CC BY 4.0 (record metadata)
# Data: 'data zenodo.xlsx' (header on row 2: Usia, Jenis kelamin, Status Menikah, then Happiness Y-1..8, Self-Esteem X2-1..10,
#   gratitude X3-1..11 with a total after each), 201 participants of the Etu ritual boxing tradition (Nagekeo, Indonesia); id = row
#   order. Ranges as observed (1-6, 1-4, 1-7).
# Covariates: age, gender, marital status.
# Dropped: three totals and trailing summary rows.
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
URL = 'https://zenodo.org/api/records/24240975/files/data%20zenodo.xlsx/content'
N_ROWS = 201
ID_COL = None
COVS = {'Unnamed: 0': 'cov_age', 'Unnamed: 1': 'cov_gender', 'Unnamed: 2': 'cov_marital'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'akhrani_2026_etu_ohq_sf': ['Y-1', 'Y-2', 'Y-3', 'Y-4', 'Y-5', 'Y-6', 'Y-7', 'Y-8'],
 'akhrani_2026_etu_rses': ['X2-1', 'X2-2', 'X2-3', 'X2-4', 'X2-5', 'X2-6', 'X2-7', 'X2-8', 'X2-9', 'X2-10'],
 'akhrani_2026_etu_gratitude': ['X3-1',
                                'X3-2',
                                'X3-3',
                                'X3-4',
                                'X3-5',
                                'X3-6',
                                'X3-7',
                                'X3-8',
                                'X3-9',
                                'X3-10',
                                'X3-11']}
# (lo, hi) response range per table
RANGES = {'akhrani_2026_etu_ohq_sf': (1, 6), 'akhrani_2026_etu_rses': (1, 4), 'akhrani_2026_etu_gratitude': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Unnamed: 11': 'happiness total', 'Unnamed: 22': 'self-esteem total', 'Unnamed: 34': 'gratitude total'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=1)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d = d[pd.to_numeric(d["Y-1"], errors="coerce").notna()].reset_index(drop=True)   # trailing total rows
    d["Unnamed: 1"] = d["Unnamed: 1"].map({"Laki-Laki": "male", "Perempuan": "female"})
    d["Unnamed: 2"] = d["Unnamed: 2"].map({"Belum menikah": "unmarried", "Sudah menikah": "married"})
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
