#!/usr/bin/env python3
# Source: https://zenodo.org/records/22700294
# DOI: 10.5281/zenodo.22700294 (data); paper 10.3390/healthcare14080973
#   Lucchini-Paredes JJ, Flores-Paredes A, Pilco-Pezo J, Peralta-Eugenio G, Sairitupa-Sanchez LZ, Morales-Garcia SB, Rivera-Lozada O, Soto-Casquero P, Morales-Garcia WC (2026). Translation and Validation of a Youth Self-Rated Insomnia Scale (YSIS) for Peruvian Adolescents. Healthcare 14(8):973. https://doi.org/10.3390/healthcare14080973. Data: https://doi.org/10.5281/zenodo.22700294
# License: CC BY 4.0 (record metadata)
# Data: YSIS_Peru_dataset_anonymized.csv, 300 Peruvian adolescents aged 13-17 from private schools; id = row order (the
#   depositor removed the original ID). YSIS_codebook.xlsx / README give the 1-5 scale.
# Covariates: sex, age, school grade. school_type is constant and not carried.
# PII: none.
# Item text: README says the YSIS item wording is not reproduced in the deposit; it is in the Healthcare paper.
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
URL = 'https://zenodo.org/api/records/22700294/files/YSIS_Peru_dataset_anonymized.csv/content'
N_ROWS = 300
ID_COL = None
COVS = {'sex': 'cov_sex', 'age': 'cov_age', 'school_grade': 'cov_school_grade'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'sairitupa_2026_ysis': ['ysis_1', 'ysis_2', 'ysis_3', 'ysis_4', 'ysis_5', 'ysis_6', 'ysis_7', 'ysis_8']}
# (lo, hi) response range per table
RANGES = {'sairitupa_2026_ysis': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'school_type': 'constant ("Private") for all 300'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{'encoding': 'utf-8-sig'})


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d["sex"] = d["sex"].map(slug)
    d["school_grade"] = d["school_grade"].map(slug)
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
