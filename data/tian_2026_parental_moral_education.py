#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/L4BGMM
# DOI: 10.7910/DVN/L4BGMM (data)
#   Tian Y (2026). Replication Data for "A Comparative Analysis of Parental Involvement in Home-Based Moral Education:
#   Effects on Early Childhood Social and Emotional Competence" [Data set]. Harvard Dataverse.
# License: CC0 1.0 (Dataverse record)
# Data: PLS_SPSS_Dataset_424_Tian.csv (format=original of the .tab), 424 Chinese parents of children under 6, the
#   deposit's own ID. Tian.sav holds the same items plus six construct means and carries no variable or value labels;
#   the PLS workbooks name no constructs either. Every item is observed on 1-5, so 1-5 (five-point) is the range.
# Tables, one per code prefix, item = the deposit's code. The record names parental feedback and children's social and
#   emotional competence; the other four prefixes are not expanded anywhere in the deposit, so their tables keep the
#   code: _scale_a (A1-6), _scale_ol (OL1-6), _feedback (F1-6; IRW's reading, from the record's "feedback of parents"),
#   _scale_s (S1-6), _scale_m (M1-6), _sec (SEC1-6, social and emotional competence).
# Covariates: cov_gender, cov_age_group, cov_ethnicity (text values in the CSV).
# PII: none (three categorical text columns).
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/13463130?format=original'
N_ROWS = 424
ID_COL = 'ID'
COVS = {'Gender': 'cov_gender', 'Age': 'cov_age_group', 'Ethnicity': 'cov_ethnicity'}
COV_MAPS = {'cov_gender': {'Female': 'female', 'Male': 'male'},
 'cov_age_group': {'Below 25 years': 'under_25',
                   '26 to 35 years': '26-35',
                   '36 to 45 years': '36-45',
                   'Above 45 years': 'over_45'},
 'cov_ethnicity': {'Han': 'han', 'Zhuang': 'zhuang', 'Hui': 'hui', 'Miao': 'miao', 'Others': 'other'}}
RENAME = {}
BLOCKS = {'tian_2026_scale_a': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6'],
 'tian_2026_scale_ol': ['OL1', 'OL2', 'OL3', 'OL4', 'OL5', 'OL6'],
 'tian_2026_feedback': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
 'tian_2026_scale_s': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6'],
 'tian_2026_scale_m': ['M1', 'M2', 'M3', 'M4', 'M5', 'M6'],
 'tian_2026_sec': ['SEC1', 'SEC2', 'SEC3', 'SEC4', 'SEC5', 'SEC6']}
# (lo, hi) response range per table
RANGES = {'tian_2026_scale_a': (1, 5),
 'tian_2026_scale_ol': (1, 5),
 'tian_2026_feedback': (1, 5),
 'tian_2026_scale_s': (1, 5),
 'tian_2026_scale_m': (1, 5),
 'tian_2026_sec': (1, 5)}
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
