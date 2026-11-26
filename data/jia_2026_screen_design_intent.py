#!/usr/bin/env python3
# Source: https://doi.org/10.1371/journal.pone.0358862.s007
# DOI: 10.1371/journal.pone.0358862.s007 (data); paper 10.1371/journal.pone.0358862
#   Jia L, Zhang Q, Zhai W, Lin Z, Li S (2026). Older adults' evaluations of smart home control screen designs: Appearance dimensions and behavioral intentions in a multi-stage study. PLOS ONE. https://doi.org/10.1371/journal.pone.0358862 (S7 Dataset, https://doi.org/10.1371/journal.pone.0358862.s007)
# License: CC BY 4.0 (record metadata)
# Data: S7 Dataset xlsx (row 1 states the scale: 1 very low .. 7 very high), 112 older adults (60+), the file's No.;
#   each of eight screen-design samples rated for liking, willingness to use and willingness to purchase.
# Table: one, 24 ratings; item = <like|use|purchase>_<sample>, read off the header.
# Covariates: gender, age band (codes from the headers).
# PII: none.
# Item text: the three questions are in the headers; the screen designs are images in the paper.
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
URL = 'https://ndownloader.figshare.com/files/69802757'
N_ROWS = 112
ID_COL = 'No.'
COVS = {'gender': 'cov_gender', 'age_band': 'cov_age_band'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'jia_2026_screen_design_intent': ['like_S9',
                                   'use_S9',
                                   'purchase_S9',
                                   'like_S46',
                                   'use_S46',
                                   'purchase_S46',
                                   'like_S56',
                                   'use_S56',
                                   'purchase_S56',
                                   'like_S69',
                                   'use_S69',
                                   'purchase_S69',
                                   'like_S73',
                                   'use_S73',
                                   'purchase_S73',
                                   'like_S80',
                                   'use_S80',
                                   'purchase_S80',
                                   'like_S81',
                                   'use_S81',
                                   'purchase_S81',
                                   'like_S86',
                                   'use_S86',
                                   'purchase_S86']}
# (lo, hi) response range per table
RANGES = {'jia_2026_screen_design_intent': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=1)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """item = <like|use|purchase>_<sample>, read off each header ("To what extent are you willing to use Sample S9?")"""
    m = {"do you like": "like", "are you willing to use": "use", "are you willing to purchase": "purchase"}
    new = list(d.columns[:3])
    for c in d.columns[3:]:
        g = re.match(r"To what extent (do you like|are you willing to use|are you willing to purchase) Sample (S[0-9]+)[?]", c)
        new.append(m[g.group(1)] + "_" + g.group(2))
    d.columns = new
    d = d.rename(columns={new[1]: "gender", new[2]: "age_band"})
    d["gender"] = d["gender"].map({1: "male", 2: "female"})
    d["age_band"] = d["age_band"].map({1: "60-65", 2: "66-70", 3: "71-75", 4: "76-80", 5: "81+"})
    assert d[["gender", "age_band"]].notna().all().all()
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
