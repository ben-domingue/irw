#!/usr/bin/env python3
# Source: https://zenodo.org/records/16777901
# DOI: 10.5281/zenodo.16777901 (data)
#   Hindarwati EN (2025). The Impact of Transformational Leadership on Innovative Work Behavior Through Knowledge Sharing
#   Using SEM: A Study of Generation Z Employees in DKI Jakarta and Banten [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: open data.xlsx, Sheet1: a blank row, then a group row naming the three constructs over their columns
#   ("Transformation Leadership" x5, "Knowledge Sharing" x3, "Innovation Work Behaviour" x4), then 446 respondents
#   (the record's N), the deposit's own Responden number; no item-level headers. Every response is within 1-5, so 1-5
#   (five-point) is the range; the record gives no anchors. A few cells are blank and stay missing.
# Tables, one per construct: _tl (transformational leadership), _ks (knowledge sharing), _iwb (innovative work
#   behaviour). The deposit has no item codes, so item = construct code + position under its group header
#   (tl1-tl5, ks1-ks3, iwb1-iwb4).
# Covariates: none in the deposit.
# PII: none (all columns numeric).
# Item text: not shipped -- no item wording in the deposit.
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
URL = 'https://zenodo.org/api/records/16777901/files/open%20data.xlsx/content'
N_ROWS = 446
ID_COL = 'Responden'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'hindarwati_2025_tl': ['tl1', 'tl2', 'tl3', 'tl4', 'tl5'],
 'hindarwati_2025_ks': ['ks1', 'ks2', 'ks3'],
 'hindarwati_2025_iwb': ['iwb1', 'iwb2', 'iwb3', 'iwb4']}
# (lo, hi) response range per table
RANGES = {'hindarwati_2025_tl': (1, 5), 'hindarwati_2025_ks': (1, 5), 'hindarwati_2025_iwb': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    raw = pd.read_excel(io.BytesIO(content), header=None)
    assert raw.iloc[0].isna().all()
    g = raw.iloc[1]
    assert g[1] == "Responden" and g[2] == "Transformation Leadership" and g[7] == "Knowledge Sharing" and g[10] == "Innovation Work Behaviour"
    assert raw.shape[1] == 14 and raw[0].isna().all()
    d = raw.iloc[2:, 1:].reset_index(drop=True)
    d.columns = ["Responden"] + [f"tl{i}" for i in range(1, 6)] + [f"ks{i}" for i in range(1, 4)] + [f"iwb{i}" for i in range(1, 5)]
    return d.dropna(how="all")


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
