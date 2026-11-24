#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Smart_Tourism_Ecosystems_The_Role_of_Music_Tourism_Drivers_and_Sustainable_Transportation_Systems_in_Singapore/32662941
# DOI: 10.6084/m9.figshare.32662941 (data)
#   Pratista A (2026). Smart Tourism Ecosystems: The Role of Music Tourism Drivers and Sustainable Transportation
#   Systems in Singapore [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: raw data.xlsx, sheet "Data Mentah": 127 respondents (Google Form), the deposit's own Responden number. Every item
#   is observed on 1-5, so 1-5 (five-point) is the range; the record gives no anchors.
# Tables (pratista_2026_music_tourism_*), one per variable block, item = the deposit's code. The deposit labels the blocks only X1, X2 and Y; the names
#   are IRW's reading of the title (two predictors, one outcome): _drivers (X1_1-8, music tourism drivers),
#   _transport (X2_1-9, sustainable transportation), _ecosystem (Y_1-10, smart tourism ecosystem). The deposit's
#   Total_X1/X2/Y are sums; not shipped.
# Covariates: none in the data sheet (the respondent profile is reported only in aggregate).
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
URL = 'https://ndownloader.figshare.com/files/65515146'
N_ROWS = 127
ID_COL = 'Responden'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'pratista_2026_music_tourism_drivers': ['X1_1', 'X1_2', 'X1_3', 'X1_4', 'X1_5', 'X1_6', 'X1_7', 'X1_8'],
 'pratista_2026_music_tourism_transport': ['X2_1', 'X2_2', 'X2_3', 'X2_4', 'X2_5', 'X2_6', 'X2_7', 'X2_8', 'X2_9'],
 'pratista_2026_music_tourism_ecosystem': ['Y_1', 'Y_2', 'Y_3', 'Y_4', 'Y_5', 'Y_6', 'Y_7', 'Y_8', 'Y_9', 'Y_10']}
# (lo, hi) response range per table
RANGES = {'pratista_2026_music_tourism_drivers': (1, 5),
 'pratista_2026_music_tourism_transport': (1, 5),
 'pratista_2026_music_tourism_ecosystem': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Total_X1': 'sum score', 'Total_X2': 'sum score', 'Total_Y': 'sum score'}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name="Data Mentah")


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
