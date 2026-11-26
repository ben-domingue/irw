#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/RUYF2S
# DOI: 10.7910/DVN/RUYF2S (data)
#   Hsiao C-H, Tang K-Y (2024). Replication Data for: From crisis to connection: Exploring the impacts of smart tourism
#   applications on international consumer's travel decision-making in Taiwan [Data set]. Harvard Dataverse.
# License: CC0 1.0 (Dataverse record)
# Data: From_crisis_to_connection-smart_tourism(n=423).csv (format=original of the .tab), 423 international visitors
#   to Taiwan, the deposit's own "#" column. Every item is observed on 1-7, so 1-7 (seven-point) is the range; the
#   record gives no anchors or construct names.
# Tables (hsiao_2024_smart_tourism_*), one per code prefix, item = the deposit's code. Names are IRW's reading of the codes in the usual IS-success
#   model for smart tourism apps; the two prefixes without an obvious expansion keep the code: _ps (PS1-3),
#   _usefulness (PU1-3), _info_quality (IQ1-3), _dq (DQ1-3), _satisfaction (SA1-3), _continuance (CI1-4).
# Covariates: cov_gender, cov_age_group, cov_education, cov_travel_freq, cov_taiwan_visits, cov_used_sta.
#   World region of origin dropped under the geographic rule.
# PII: none (seven categorical text columns).
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/10409664?format=original'
N_ROWS = 423
ID_COL = '#'
COVS = {'Gender': 'cov_gender',
 'Age': 'cov_age_group',
 'Education': 'cov_education',
 'Travel frequency': 'cov_travel_freq',
 'How many times have you come to Taiwan?': 'cov_taiwan_visits',
 'Have you ever used any forms of STA (e': 'cov_used_sta'}
COV_MAPS = {'cov_gender': {'Female': 'female', 'Male': 'male'},
 'cov_age_group': {'10s and below (~19)': '19_or_under',
                   '20s (20~29)': '20-29',
                   '30s (30~39)': '30-39',
                   '40s (40~49)': '40-49',
                   '50s and above (50~)': '50+'},
 'cov_education': {'High school or below': 'high_school_or_below',
                   'College or Undergraduate school': 'undergraduate',
                   'Graduate school and above': 'graduate'},
 'cov_travel_freq': {'More than once a month': 'monthly_plus',
                     'Once in 3 months': 'every_3_months',
                     'Once in 6 months': 'every_6_months',
                     'Once a year or below': 'yearly_or_less'},
 'cov_taiwan_visits': {'Once or below': 'once_or_less', 'Twice': 'twice', 'More than three times': 'more_than_three'},
 'cov_used_sta': {'Yes': 'yes', 'Never': 'never'}}
RENAME = {}
BLOCKS = {'hsiao_2024_smart_tourism_ps': ['PS1', 'PS2', 'PS3'],
 'hsiao_2024_smart_tourism_usefulness': ['PU1', 'PU2', 'PU3'],
 'hsiao_2024_smart_tourism_info_quality': ['IQ1', 'IQ2', 'IQ3'],
 'hsiao_2024_smart_tourism_dq': ['DQ1', 'DQ2', 'DQ3'],
 'hsiao_2024_smart_tourism_satisfaction': ['SA1', 'SA2', 'SA3'],
 'hsiao_2024_smart_tourism_continuance': ['CI1', 'CI2', 'CI3', 'CI4']}
# (lo, hi) response range per table
RANGES = {'hsiao_2024_smart_tourism_ps': (1, 7),
 'hsiao_2024_smart_tourism_usefulness': (1, 7),
 'hsiao_2024_smart_tourism_info_quality': (1, 7),
 'hsiao_2024_smart_tourism_dq': (1, 7),
 'hsiao_2024_smart_tourism_satisfaction': (1, 7),
 'hsiao_2024_smart_tourism_continuance': (1, 7)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Which region are you from?': 'geographic, dropped'}


def load(content):
    return pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")


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
