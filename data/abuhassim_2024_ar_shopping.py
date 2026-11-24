#!/usr/bin/env python3
# Source: https://zenodo.org/records/12596211
# DOI: 10.5281/zenodo.12596211 (data)
#   Abu Hassim A (2024). AR Apps in Online Shopping [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: AR Apps Data.csv, 420 respondents, the deposit's own ID column. The record has no description, codebook or
#   anchors; every item is observed within 1-5, so 1-5 (five-point) is taken as the range.
# Tables, one per code prefix, item = the deposit's code. Construct names are IRW's reading of the codes, which follow
#   the usual hedonic/utilitarian-value -> attitude -> intention model for AR shopping apps: _hedonic_value (PHV1-5),
#   _utilitarian_value (PUV1-5), _ba (BA1-4; the construct behind "BA" is not stated anywhere in the deposit, so the
#   code is kept), _attitude (ATT1-2), _intention (BI1-3, behavioural intention).
# Covariates: none in the deposit.
# PII: none (all columns numeric).
# Item text: not shipped -- codes only in the deposit.
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
URL = 'https://zenodo.org/api/records/12596211/files/AR%20Apps%20Data.csv/content'
N_ROWS = 420
ID_COL = 'ID'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'abuhassim_2024_hedonic_value': ['PHV1', 'PHV2', 'PHV3', 'PHV4', 'PHV5'],
 'abuhassim_2024_utilitarian_value': ['PUV1', 'PUV2', 'PUV3', 'PUV4', 'PUV5'],
 'abuhassim_2024_ba': ['BA1', 'BA2', 'BA3', 'BA4'],
 'abuhassim_2024_attitude': ['ATT1', 'ATT2'],
 'abuhassim_2024_intention': ['BI1', 'BI2', 'BI3']}
# (lo, hi) response range per table
RANGES = {'abuhassim_2024_hedonic_value': (1, 5),
 'abuhassim_2024_utilitarian_value': (1, 5),
 'abuhassim_2024_ba': (1, 5),
 'abuhassim_2024_attitude': (1, 5),
 'abuhassim_2024_intention': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_csv(io.BytesIO(content))


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
