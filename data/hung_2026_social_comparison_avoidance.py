#!/usr/bin/env python3
# Source: https://zenodo.org/records/23951310
# DOI: 10.5281/zenodo.23951310 (data)
#   Hung (2026). Digital Social Comparison and Social Avoidance Among Chinese Adolescents: A Four-Wave Study of Problematic Social Media Use [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23951310
# License: CC BY 4.0 (record metadata)
# Data: SPSS.sav, 748 Chinese adolescents aged 14-18 (one wave of the four-wave study); id = row order. Variable labels
#   carry the English stems of every item; all items 1-7.
# Tables: one per construct; EX = five impression-management items (dichotomised copies Exp1-5 and their mean SDR not shipped).
# Covariates: gender, age, ethnicity code, grade, parental education, retained/attrited flag (group: 0 retained, 1 lost).
# PII: none.
# Item text: all six tables held 2026-11-25 (automated_finding/itemtext_hold_2026-11-25.csv) -- named third-party scales
#   (MC-SDS, RCBS-, BSMAS-style, comparison items); English labels in the .sav;
#   automated_finding/itemtext_verification/make_itemtext_repos_2026-11-25c.py
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
URL = 'https://zenodo.org/api/records/23951310/files/SPSS.sav/content'
N_ROWS = 748
ID_COL = None
COVS = {'Gender': 'cov_gender',
 'Age': 'cov_age',
 'Ethnicity': 'cov_ethnicity',
 'Grade': 'cov_grade',
 'F_EDU': 'cov_father_edu',
 'M_EDU': 'cov_mother_edu',
 'group': 'cov_attrited'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'hung_2026_social_avoidance': ['SA1', 'SA2', 'SA3', 'SA4', 'SA5'],
 'hung_2026_psmu': ['PSMU1', 'PSMU2', 'PSMU3', 'PSMU4', 'PSMU5', 'PSMU6'],
 'hung_2026_upward_comparison': ['USC1', 'USC2', 'USC3', 'USC4', 'USC5', 'USC6'],
 'hung_2026_downward_comparison': ['DSC7', 'DSC8', 'DSC9', 'DSC10', 'DSC11', 'DSC12'],
 'hung_2026_shyness': ['SHY1', 'SHY2', 'SHY3', 'SHY4', 'SHY5', 'SHY6'],
 'hung_2026_social_desirability': ['EX1', 'EX2', 'EX3', 'EX4', 'EX5']}
# (lo, hi) response range per table
RANGES = {'hung_2026_social_avoidance': (1, 7),
 'hung_2026_psmu': (1, 7),
 'hung_2026_upward_comparison': (1, 7),
 'hung_2026_downward_comparison': (1, 7),
 'hung_2026_shyness': (1, 7),
 'hung_2026_social_desirability': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'SA': 'mean score',
 'PSMU': 'mean score',
 'USC': 'mean score',
 'DSC': 'mean score',
 'SHY': 'mean score',
 'Exp1': 'dichotomised copy of EX (7 = 1)',
 'Exp2': 'dichotomised copy of EX (7 = 1)',
 'Exp3': 'dichotomised copy of EX (7 = 1)',
 'Exp4': 'dichotomised copy of EX (7 = 1)',
 'Exp5': 'dichotomised copy of EX (7 = 1)',
 'SDR': 'mean of the Exp dummies',
 'number': 'row number'}
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
