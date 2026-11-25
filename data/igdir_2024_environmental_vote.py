#!/usr/bin/env python3
# Source: https://zenodo.org/records/24463648
# DOI: 10.5281/zenodo.24463648 (data)
#   Anonymous (2026). Environmental risk perception and environmental vote salience among university students in Igdir, Turkiye: survey dataset and supplementary analysis code (N = 532, 2024) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24463648
# License: CC BY 4.0 (record metadata)
# Data: igdir_survey_data.csv, 532 university students in Igdir, Turkiye (2024), the file's id; igdir_survey_codebook.csv
#   describes every column (Likert 1-5 for the CB, CA, PD and MS items; single-item ratings and codes for the rest).
#   Depositor anonymous on the record, so the table names use the place and year.
# Tables: one per item prefix in the codebook (item order sorted; the file stores them shuffled).
# Covariates: gender, age, faculty code, education level, income band, and four single-item ratings/codes.
# Not shipped: the ten knowledge items (raw option codes, no key), six nominal party evaluations, region (geographic).
# PII: none.
# Item text: the codebook gives only one-line glosses for CB/CA/PD/MS ("environmental risk perception item"); wording not in the deposit.
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
URL = 'https://zenodo.org/api/records/24463648/files/igdir_survey_data.csv/content'
N_ROWS = 532
ID_COL = 'id'
COVS = {'gender': 'cov_gender',
 'age': 'cov_age',
 'faculty': 'cov_faculty',
 'education': 'cov_education',
 'income': 'cov_income_band',
 'winter_air_quality': 'cov_winter_air_rating',
 'health_effects_known': 'cov_pollution_health_aware',
 'top_env_problem': 'cov_top_env_problem',
 'trust_promises': 'cov_trust_env_promises'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'igdir_2024_env_risk': ['CB1', 'CB2', 'CB3', 'CB4', 'CB5', 'CB6'],
 'igdir_2024_env_political_response': ['CA1', 'CA2', 'CA3', 'CA4', 'CA5', 'CA6', 'CA7', 'CA8', 'CA9', 'CA10'],
 'igdir_2024_admin_performance': ['PD1', 'PD2'],
 'igdir_2024_media_scepticism': ['MS1', 'MS2']}
# (lo, hi) response range per table
RANGES = {'igdir_2024_env_risk': (1, 5),
 'igdir_2024_env_political_response': (1, 5),
 'igdir_2024_admin_performance': (1, 5),
 'igdir_2024_media_scepticism': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'kq1': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq2': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq3': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq4': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq5': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq6': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq7': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq8': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq9': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'kq10': 'climate-knowledge multiple choice, raw option codes; the answer key is not in the deposit',
 'party_AKP': 'nominal party-policy evaluation (favourable / unfavourable / no opinion)',
 'party_CHP': 'nominal party-policy evaluation (favourable / unfavourable / no opinion)',
 'party_MHP': 'nominal party-policy evaluation (favourable / unfavourable / no opinion)',
 'party_IYI': 'nominal party-policy evaluation (favourable / unfavourable / no opinion)',
 'party_DEM': 'nominal party-policy evaluation (favourable / unfavourable / no opinion)',
 'party_SP': 'nominal party-policy evaluation (favourable / unfavourable / no opinion)',
 'awareness_score': 'count of correct knowledge answers (composite)',
 'region_origin': 'region of origin (geographic)'}


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{})


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d["gender"] = d["gender"].map({1: "woman", 2: "man"})
    d["education"] = d["education"].map({1: "associate", 2: "undergraduate"})
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
