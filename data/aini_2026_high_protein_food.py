#!/usr/bin/env python3
# Source: https://zenodo.org/records/23295180
# DOI: 10.5281/zenodo.23295180 (data)
#   Aini N (2026). Decoding Online Purchase Intention toward High-Protein Food Products [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23295180
# License: CC BY 4.0 (record metadata)
# Data: Google Forms export, 138 Indonesian respondents; id = row order. No codes: each header is the full Indonesian
#   stem. The record has no description; blocks are IRW's reading of the stems in file order (social-media content 1-6,
#   consumer reviews 7-13, health benefit (hb) 14-20, value 21-23, purchase intention 24-27). Every item observed within 1-5.
# Item codes are positional within each block (smm1 = 2nd header .. purchase_intention4 = last).
# Covariate: the first column (how often the respondent buys food/drink online, 1-5).
# PII: none.
# Item text: shipped 2026-11-25c -- Indonesian stems = the headers, tied by this script's positional slicing, IRW
#   English; automated_finding/itemtext_verification/make_itemtext_repos_2026-11-25c.py
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
URL = 'https://zenodo.org/api/records/23295180/files/Decoding%20Online%20Purchase%20Intention%20toward%20High-Protein%20Food%20Products.xlsx/content'
N_ROWS = 138
ID_COL = None
COVS = {'freq': 'cov_online_food_purchase_freq'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'aini_2026_smm': ['smm1', 'smm2', 'smm3', 'smm4', 'smm5', 'smm6'],
 'aini_2026_reviews': ['reviews1', 'reviews2', 'reviews3', 'reviews4', 'reviews5', 'reviews6', 'reviews7'],
 'aini_2026_health_benefit': ['hb1', 'hb2', 'hb3', 'hb4', 'hb5', 'hb6', 'hb7'],
 'aini_2026_value': ['value1', 'value2', 'value3'],
 'aini_2026_purchase_intention': ['purchase_intention1',
                                  'purchase_intention2',
                                  'purchase_intention3',
                                  'purchase_intention4']}
# (lo, hi) response range per table
RANGES = {'aini_2026_smm': (1, 5),
 'aini_2026_reviews': (1, 5),
 'aini_2026_health_benefit': (1, 5),
 'aini_2026_value': (1, 5),
 'aini_2026_purchase_intention': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """the Google-Forms headers are the full Indonesian stems; item k of a block = the k-th header in file order"""
    cols = list(d.columns)
    new = ["freq"]
    for n, a, b in [('smm', 1, 7), ('reviews', 7, 14), ('hb', 14, 21), ('value', 21, 24), ('purchase_intention', 24, 28)]:
        new += [f"{n}{i - a + 1}" for i in range(a, b)]
    assert len(new) == len(cols) == 28, len(cols)
    d.columns = new
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
