#!/usr/bin/env python3
# Source: https://zenodo.org/records/24404396
# DOI: 10.5281/zenodo.24404396 (data)
#   Dursun M, Ulun C, Can HC, Aktas Ustun N (2026). Mediating role of mental well-being in the relationship between career decisiveness and happiness among sports science students [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24404396
# License: CC BY 4.0 (record metadata)
# Data: one .sav, 311 sport-science students at four Turkish universities; id = row order. K1-6 career decisiveness, Warwick_M1-7 (SWEMWBS),
#   OXF_M1-7 (Oxford happiness, 7 items), all 1-5.
# Covariates: gender, age, university, department, year, income, satisfaction with department, career thought, reason, does sport (codes).
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
URL = 'https://zenodo.org/api/records/24404396/files/Kariyer_Kar_Mut_mio_2025_Arac%C4%B1_Model.sav/content'
N_ROWS = 311
ID_COL = None
COVS = {'Cinsiyet': 'cov_gender',
 'Yaş': 'cov_age',
 'Üniversite': 'cov_university',
 'Bölüm': 'cov_department',
 'Sınıf': 'cov_year',
 'Gelir': 'cov_income',
 'Memnunmusun': 'cov_satisfied_department',
 'Düşüncen': 'cov_career_thought',
 'Sebep': 'cov_reason',
 'Sporyapma': 'cov_does_sport'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'dursun_2026_career_decisiveness': ['K1', 'K2', 'K3', 'K4', 'K5', 'K6'],
 'dursun_2026_swemwbs': ['Warwick_M1',
                         'Warwick_M2',
                         'Warwick_M3',
                         'Warwick_M4',
                         'Warwick_M5',
                         'Warwick_M6',
                         'Warwick_M7'],
 'dursun_2026_ohq_short': ['OXF_M1', 'OXF_M2', 'OXF_M3', 'OXF_M4', 'OXF_M5', 'OXF_M6', 'OXF_M7']}
# (lo, hi) response range per table
RANGES = {'dursun_2026_career_decisiveness': (1, 5), 'dursun_2026_swemwbs': (1, 5), 'dursun_2026_ohq_short': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Fakülte': 'constant',
 'Sıra': 'row-order string (questionnaire version label)',
 'X_Kariyer': 'scale score',
 'M_MİO': 'scale score',
 'Y_MUT': 'scale score'}
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
