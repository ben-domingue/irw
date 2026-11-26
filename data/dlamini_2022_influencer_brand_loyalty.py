#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/269pfcstyt
# DOI: 10.17632/269pfcstyt (data)
#   Dlamini S (2022). The Impact of Social Media Influencers on Fashion Brand Loyalty DATA [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: one workbook, sheet "Data" (252 respondents) plus a "Coding" sheet that names every construct and gives the
#   anchors (1 = Strongly Disagree ... 5 = Strongly Agree) and the demographic codes.
# Tables, one per construct, item = the deposit's code: _expertise (PE1-4, perceived expertise), _congruence (PC1-4,
#   perceived congruence), _authenticity (AU1-4), _trust (T1-6), _attitude_influencer (AT1-4), _brand_attitude
#   (BA1-5), _brand_loyalty (BL1-6). id = the deposit's NUMBER column.
# Covariates: cov_gender (G1: 1 male, 2 female, 3 other, 4 prefer not to say), cov_social_media_freq (F1, coded per the
#   Coding sheet). C1-C3 are screeners answered 1 (yes) by everyone, not carried.
# PII: none (all columns numeric).
# Item text: not shipped -- the Coding sheet names the constructs and anchors but not the item stems.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://data.mendeley.com/public-files/datasets/269pfcstyt/files/39f34fde-d371-43cd-b7c4-8b979377ef60/file_downloaded'
N_ROWS = 252
ID_COL = 'NUMBER'
COVS = {'G1': 'cov_gender', 'F1': 'cov_social_media_freq'}
COV_MAPS = {'cov_gender': {1: 'male', 2: 'female', 3: 'other', 4: 'prefer_not_to_say'},
 'cov_social_media_freq': {1: 'more_than_once_a_day',
                           2: 'once_a_day',
                           3: 'most_days_a_week',
                           4: 'once_a_week',
                           5: 'once_a_month_or_less'}}
RENAME = {}
BLOCKS = {'dlamini_2022_expertise': ['PE1', 'PE2', 'PE3', 'PE4'],
 'dlamini_2022_congruence': ['PC1', 'PC2', 'PC3', 'PC4'],
 'dlamini_2022_authenticity': ['AU1', 'AU2', 'AU3', 'AU4'],
 'dlamini_2022_trust': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
 'dlamini_2022_attitude_influencer': ['AT1', 'AT2', 'AT3', 'AT4'],
 'dlamini_2022_brand_attitude': ['BA1', 'BA2', 'BA3', 'BA4', 'BA5'],
 'dlamini_2022_brand_loyalty': ['BL1', 'BL2', 'BL3', 'BL4', 'BL5', 'BL6']}
# (lo, hi) response range per table
RANGES = {'dlamini_2022_expertise': (1, 5),
 'dlamini_2022_congruence': (1, 5),
 'dlamini_2022_authenticity': (1, 5),
 'dlamini_2022_trust': (1, 5),
 'dlamini_2022_attitude_influencer': (1, 5),
 'dlamini_2022_brand_attitude': (1, 5),
 'dlamini_2022_brand_loyalty': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'C1': 'screener, constant', 'C2': 'screener, constant', 'C3': 'screener, constant'}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name="Data")


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
    assert len(d) == N_ROWS, len(d)
    d = d.rename(columns=RENAME)
    d = prep(d)
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
    covs = list(COVS.values())
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
