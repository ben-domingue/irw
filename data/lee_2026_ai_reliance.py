#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/O4E9YN
# DOI: 10.7910/DVN/O4E9YN (data)
#   Lee H (2026). The Adaptive Paradox of AI Reliance: Control, Trust, Creepiness, and Reliance Patterns [Data set]. Dataverse. https://doi.org/10.7910/DVN/O4E9YN
# License: CC0 1.0 (record metadata)
# Data: Data.xlsx, sheet Data, 502 respondents, the file's respondent_id. The Codebook sheet gives each item's construct,
#   English wording and the scale (1 = strongly disagree .. 5 = strongly agree). A04 and C04 are absent from the data.
# Tables: one per codebook construct (nine).
# Covariates: gender, age group, education, occupation, AI-use frequency.
# PII: none.
# Item text: shipped 2026-11-25c for 7 constructs (Codebook sheet); mastery (Pearlin) and self_esteem (CSES/RSES mix)
#   held 2026-11-25 (automated_finding/itemtext_hold_2026-11-25.csv);
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/14255189'
N_ROWS = 502
ID_COL = 'respondent_id'
COVS = {'gender': 'cov_gender',
 'age_group': 'cov_age_band',
 'education': 'cov_education',
 'occupation': 'cov_occupation',
 'ai_use_frequency': 'cov_ai_use_freq'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'lee_2026_meaning_making': ['A01', 'A02', 'A03', 'A05'],
 'lee_2026_mastery': ['B01', 'B02', 'B03', 'B04', 'B05'],
 'lee_2026_self_esteem': ['C01', 'C02', 'C03', 'C05'],
 'lee_2026_perceived_control': ['D01', 'D02', 'D03'],
 'lee_2026_trust_in_ai': ['E01', 'E02', 'E03', 'E04'],
 'lee_2026_creepiness': ['F01', 'F02', 'F03', 'F04'],
 'lee_2026_task_oriented_reliance': ['G01', 'G02', 'G03', 'G04'],
 'lee_2026_overreliance': ['H01', 'H02', 'H03', 'H04'],
 'lee_2026_ai_avoidance': ['I01', 'I02', 'I03', 'I04']}
# (lo, hi) response range per table
RANGES = {'lee_2026_meaning_making': (1, 5),
 'lee_2026_mastery': (1, 5),
 'lee_2026_self_esteem': (1, 5),
 'lee_2026_perceived_control': (1, 5),
 'lee_2026_trust_in_ai': (1, 5),
 'lee_2026_creepiness': (1, 5),
 'lee_2026_task_oriented_reliance': (1, 5),
 'lee_2026_overreliance': (1, 5),
 'lee_2026_ai_avoidance': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Data', header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    for c in ["gender", "education", "occupation", "ai_use_frequency"]:
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
