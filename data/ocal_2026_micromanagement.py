#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_on_Micromanagement_Psychological_Safety_Organizational_Silence_and_Innovative_Work_Behavior/33477391
# DOI: 10.6084/m9.figshare.33477391 (data)
#   Öcal Z (2026). Dataset on Micromanagement, Psychological Safety, Organizational Silence, and Innovative Work
#   Behavior [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: dataset.xlsx, sheet Sayfa1: 216 Turkish employees (online and face-to-face), the deposit's own participant no.
#   The worksheet has 1,000 rows; the rows after the last participant are empty and are dropped. codebook.xlsx gives
#   every demographic code and the scale: 1 = Strongly disagree ... 5 = Strongly agree. Item cells are blank where a
#   respondent skipped and stay missing.
# Tables, one per construct, item = the deposit's code: _micromanagement (MM1-13), _psych_safety (PS1-7),
#   _org_silence (OS1-7, OS9-16), _innovative_work (IWB1-9). OS8 is labelled "OS8 (control)" in the header, a control
#   item rather than a silence item, and is not shipped.
# Covariates (codebook): cov_mode (data style), cov_gender, cov_age_group, cov_marital, cov_education, cov_position,
#   cov_tenure, cov_sector, cov_firm_size.
# PII: none (all columns numeric).
# Item text: not shipped -- the codebook names each item only as "<construct> item k".
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
URL = 'https://ndownloader.figshare.com/files/68350897'
N_ROWS = 216
ID_COL = 'participant no'
COVS = {'data style': 'cov_mode',
 'gender': 'cov_gender',
 'age': 'cov_age_group',
 'marital status': 'cov_marital',
 'education': 'cov_education',
 'position': 'cov_position',
 'tenure': 'cov_tenure',
 'sector': 'cov_sector',
 'number of employees': 'cov_firm_size'}
COV_MAPS = {'cov_mode': {1: 'online', 2: 'face_to_face'},
 'cov_gender': {1: 'male', 2: 'female'},
 'cov_age_group': {1: '18-24', 2: '25-44', 3: '45-54', 4: '55-64', 5: '65+'},
 'cov_marital': {1: 'married', 2: 'widowed', 3: 'divorced', 4: 'separated', 5: 'never_married'},
 'cov_education': {1: 'high_school', 2: 'associate', 3: 'bachelor', 4: 'master_or_phd'},
 'cov_position': {1: 'manager', 2: 'specialist', 3: 'technical', 4: 'support', 5: 'intern'},
 'cov_tenure': {1: 'under_1_month', 2: 'under_1_year', 3: '1-3_years', 4: '4-6_years', 5: '7_plus_years'},
 'cov_sector': {1: 'software',
                2: 'electrical',
                3: 'defence',
                4: 'biotech',
                5: 'energy_environment',
                6: 'automotive',
                7: 'other'},
 'cov_firm_size': {1: '1-10', 2: '11-50', 3: '51-250', 4: '251+'}}
RENAME = {}
BLOCKS = {'ocal_2026_micromanagement': ['MM1',
                               'MM2',
                               'MM3',
                               'MM4',
                               'MM5',
                               'MM6',
                               'MM7',
                               'MM8',
                               'MM9',
                               'MM10',
                               'MM11',
                               'MM12',
                               'MM13'],
 'ocal_2026_psych_safety': ['PS1', 'PS2', 'PS3', 'PS4', 'PS5', 'PS6', 'PS7'],
 'ocal_2026_org_silence': ['OS1',
                           'OS2',
                           'OS3',
                           'OS4',
                           'OS5',
                           'OS6',
                           'OS7',
                           'OS9',
                           'OS10',
                           'OS11',
                           'OS12',
                           'OS13',
                           'OS14',
                           'OS15',
                           'OS16'],
 'ocal_2026_innovative_work': ['IWB1', 'IWB2', 'IWB3', 'IWB4', 'IWB5', 'IWB6', 'IWB7', 'IWB8', 'IWB9']}
# (lo, hi) response range per table
RANGES = {'ocal_2026_micromanagement': (1, 5),
 'ocal_2026_psych_safety': (1, 5),
 'ocal_2026_org_silence': (1, 5),
 'ocal_2026_innovative_work': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'OS8 (control)': 'control item, not a silence item'}


def load(content):
    d = pd.read_excel(io.BytesIO(content), sheet_name="Sayfa1")
    d.columns = [str(c).strip() for c in d.columns]
    return d[d["participant no"].notna()].copy()


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
