#!/usr/bin/env python3
# Source: https://zenodo.org/records/24394750
# DOI: 10.5281/zenodo.24394750 (data)
#   Kuyu SI, Armutcu V (2026). From Perfectionism to Compulsive Buying: The Influence of Social Appearance Anxiety and Self-Esteem [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24394750
# License: CC BY 4.0 (record metadata)
# Data: Data.csv, 346 adults in Turkey, the deposit's ID. No codebook or anchors in the record; ranges are as observed
#   (FMPS, CBS, SAAS 1-5; SCS 1-6).
# Tables: one per instrument code. Covariates: the nine demographic columns as numeric codes (the deposit does not
#   document the codes; age is in years).
# PII: none.
# Item text: codes only in the deposit.
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
URL = 'https://zenodo.org/api/records/24394750/files/Data.csv/content'
N_ROWS = 346
ID_COL = 'ID'
COVS = {'Gender': 'cov_gender',
 'Age': 'cov_age',
 'Education': 'cov_education',
 'Marital_Status': 'cov_marital_status',
 'Occupation': 'cov_occupation',
 'Monthly_Household_Income': 'cov_monthly_household_income',
 'Place_of_Residence': 'cov_place_of_residence',
 'Shopping_Frequency': 'cov_shopping_frequency',
 'Spending_Category': 'cov_spending_category'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'kuyu_2026_perfectionism': ['FMPS1',
                             'FMPS2',
                             'FMPS3',
                             'FMPS4',
                             'FMPS5',
                             'FMPS6',
                             'FMPS7',
                             'FMPS8',
                             'FMPS9',
                             'FMPS10',
                             'FMPS11',
                             'FMPS12',
                             'FMPS13',
                             'FMPS14',
                             'FMPS15',
                             'FMPS16',
                             'FMPS17',
                             'FMPS18',
                             'FMPS19',
                             'FMPS20',
                             'FMPS21',
                             'FMPS22',
                             'FMPS23',
                             'FMPS24',
                             'FMPS25',
                             'FMPS26',
                             'FMPS27',
                             'FMPS28',
                             'FMPS29',
                             'FMPS30',
                             'FMPS31',
                             'FMPS32',
                             'FMPS33',
                             'FMPS34',
                             'FMPS35'],
 'kuyu_2026_compulsive_buying': ['CBS1',
                                 'CBS2',
                                 'CBS3',
                                 'CBS4',
                                 'CBS5',
                                 'CBS6',
                                 'CBS7',
                                 'CBS8',
                                 'CBS9',
                                 'CBS10',
                                 'CBS11',
                                 'CBS12'],
 'kuyu_2026_scs': ['SCS1',
                   'SCS2',
                   'SCS3',
                   'SCS4',
                   'SCS5',
                   'SCS6',
                   'SCS7',
                   'SCS8',
                   'SCS9',
                   'SCS10',
                   'SCS11',
                   'SCS12',
                   'SCS13',
                   'SCS14',
                   'SCS15',
                   'SCS16',
                   'SCS17',
                   'SCS18'],
 'kuyu_2026_saas': ['SAAS1',
                    'SAAS2',
                    'SAAS3',
                    'SAAS4',
                    'SAAS5',
                    'SAAS6',
                    'SAAS7',
                    'SAAS8',
                    'SAAS9',
                    'SAAS10',
                    'SAAS11',
                    'SAAS12',
                    'SAAS13',
                    'SAAS14',
                    'SAAS15',
                    'SAAS16']}
# (lo, hi) response range per table
RANGES = {'kuyu_2026_perfectionism': (1, 5),
 'kuyu_2026_compulsive_buying': (1, 5),
 'kuyu_2026_scs': (1, 6),
 'kuyu_2026_saas': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{})


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
