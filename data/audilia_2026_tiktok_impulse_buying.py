#!/usr/bin/env python3
# Source: https://zenodo.org/records/23913988
# DOI: 10.5281/zenodo.23913988 (data)
#   Audilia E, Iswara L, Anggraeni A (2026). From Social Presence to Impulse Buying: A Study of Indonesian TikTok Live
#   Shopping [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: EALIAA WAS2026.xlsx, 150 Indonesian TikTok Live shoppers, the deposit's own ID column. Items are observed on 1-6;
#   the record gives no anchors, so 1-6 (six-point) is taken as the range.
# Tables, one per construct, item = the deposit's code. Construct names are IRW's reading of the codes against the
#   title (social presence -> pleasure/arousal -> impulse buying, an S-O-R model): _sp_buyers (SPOB-1..3, social
#   presence of other buyers), _sp_viewers (SPOV-1..3), _sp_streamer (SPOLS-1..3, of the live streamer), _pleasure
#   (P-1..3), _arousal (A-1..3), _impulse_buying (IB-1..3).
# Covariates: none. Residence, Age, Gender, Occupation, Experience, TikTok experience, Frequency and Product category
#   are numeric codes with no key in the deposit, so they are not carried.
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
URL = 'https://zenodo.org/api/records/23913988/files/EALIAA%20WAS2026.xlsx/content'
N_ROWS = 150
ID_COL = 'ID'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'audilia_2026_sp_buyers': ['SPOB-1', 'SPOB-2', 'SPOB-3'],
 'audilia_2026_sp_viewers': ['SPOV-1', 'SPOV-2', 'SPOV-3'],
 'audilia_2026_sp_streamer': ['SPOLS-1', 'SPOLS-2', 'SPOLS-3'],
 'audilia_2026_pleasure': ['P-1', 'P-2', 'P-3'],
 'audilia_2026_arousal': ['A-1', 'A-2', 'A-3'],
 'audilia_2026_impulse_buying': ['IB-1', 'IB-2', 'IB-3']}
# (lo, hi) response range per table
RANGES = {'audilia_2026_sp_buyers': (1, 6),
 'audilia_2026_sp_viewers': (1, 6),
 'audilia_2026_sp_streamer': (1, 6),
 'audilia_2026_pleasure': (1, 6),
 'audilia_2026_arousal': (1, 6),
 'audilia_2026_impulse_buying': (1, 6)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Residence': 'unkeyed code',
 'Age': 'unkeyed code',
 'Gender': 'unkeyed code',
 'Occupation': 'unkeyed code',
 'Experience': 'unkeyed code',
 'Tiktok Experience': 'unkeyed code',
 'Frequency': 'unkeyed code',
 'Product category': 'unkeyed code'}


def load(content):
    return pd.read_excel(io.BytesIO(content))


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
