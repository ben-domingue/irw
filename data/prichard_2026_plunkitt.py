#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ICPVD0
# DOI: 10.7910/DVN/ICPVD0 (data)
#   Prichard E (2026). Plunkitt Personality Inventory and Populism Support Data [Data set]. Dataverse. https://doi.org/10.7910/DVN/ICPVD0
# License: CC0 1.0 (record metadata)
# Data: 'Plunkitt1 2.xlsx', 300 U.S. adults; id = row order. Column headers are the question wording with spaces
#   removed (e.g. 'Howessentialdoyoubelievepatronageisinpolitics1Notessentialatall'); item = the header, leading space stripped.
# Tables: PPI (12 items, 1-7), populism (12 items, 1-10), policy agreement (5 items, 1-7).
# Covariates: gender, age, eligible-voter flag, political orientation (1 very left .. 7 very right; one item, so a covariate).
# Dropped: Populism and PPI (sum scores).
# PII: none.
# Item text: stems are compressed into the column headers (spaces removed); the full wording would need the instrument.
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/14448947'
N_ROWS = 300
ID_COL = None
COVS = {'WhatisYourGender': 'cov_gender',
 'WhatisYourAgeinNumbersEx43': 'cov_age',
 'IamaU.S.citizenandlegallyeligibletovoteintheU.S': 'cov_us_eligible_voter',
 'Howwouldyourateyourpoliticalorientationfrom1VeryLeftLeaningto7Ve': 'cov_political_orientation'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'prichard_2026_plunkitt_ppi': ['Howessentialdoyoubelievepatronageisinpolitics1Notessentialatall',
                                'Towhatextentdoyouvaluepoliticalalliancesandpartnerships1Notvalua',
                                'Howbeneficialdoyouconsiderpoliticalmachinestobe1Notbeneficial',
                                'Howacceptabledoyoufindpoliticalfavorsandexchanges1Completelyunac',
                                'Towhatextentdoyouagreewiththeconceptofhonestgraftinpolitics1Stro',
                                'Howacceptableisittousepublicfundsforpersonalgaininpolitics1Compl',
                                'Howbeneficialdoyouviewtherelationshipbetweenbusinessandpolitics1',
                                'Howeffectivedoyouconsidertraditionalpoliticalstrategiestobe1Note',
                                'Howimportantdoyouthinkloyaltyisinpolitics1Notimportant7Extremely',
                                'Howacceptabledoyoufindpoliticalnepotism1Completelyunacceptable7C',
                                'Howacceptableistheuseoffavorsinpoliticalnegotiations1Completelyu',
                                'Howacceptableisittousepoliticalinfluenceforpersonalgain1Complete'],
 'prichard_2026_populism': ['Somepeoplesay',
                            'Therearethosewho',
                            'Somepeoplesay_A',
                            'Somepeoplesay_B',
                            'Somepeoplesay_C',
                            'Therearethosewhosaythatconflicts',
                            'Accordingtosomepeoplethejobof',
                            'Therearethosewho_A',
                            'Somepeoplethinkthatinpoliticsyou',
                            'SomepeoplethinkthatCongressas',
                            'Therearethose',
                            'Therearethosewho_B'],
 'prichard_2026_policy_attitudes': ['Rateyourlevelofagreementwiththefollowingstatementfrom1StronglyDi',
                                    'Rateyourlevelofagreementwiththefollowingstatementfrom1Strongly_A',
                                    'Rateyourlevelofagreementwiththefollowingstatementfrom1Strongly_B',
                                    'Rateyourlevelofagreementwiththefollowingstatementfrom1Strongly_C',
                                    'Rateyourlevelofagreementwiththefollowingstatementfrom1Strongly_D']}
# (lo, hi) response range per table
RANGES = {'prichard_2026_plunkitt_ppi': (1, 7), 'prichard_2026_populism': (1, 10), 'prichard_2026_policy_attitudes': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Populism': 'scale sum', 'PPI': 'scale sum'}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d["WhatisYourGender"] = d["WhatisYourGender"].map(slug)
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
