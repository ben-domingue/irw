#!/usr/bin/env python3
# Source: https://zenodo.org/records/24036100
# DOI: 10.5281/zenodo.24036100 (data)
#   Ding X (2026). Online-Offline Authenticity Congruence and Discrepancy in Adolescents: Associations with Mental Health and AI Dependence [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24036100
# License: CC BY 4.0 (record metadata)
# Data: 'data RSA.xlsx', 1,464 Chinese adolescents aged 10-18 from two sources, the file's case_id. No codebook; blocks and
#   ranges read from the column names and the derived totals beside them (who5_total 0-25, phq4_total 0-12, rfqy_* means).
# Tables: one per item block. The attention-check flag and response are carried as covariates, not used to filter.
# Covariates: source, gender, age, internet / social-media time, AI frequency, single-item loneliness, attention check.
# Dropped: all totals and means.
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
URL = 'https://zenodo.org/api/records/24036100/files/data%20RSA.xlsx/content'
N_ROWS = 1464
ID_COL = 'case_id'
COVS = {'source_code': 'cov_source',
 'attention check': 'cov_attention_pass',
 'gender': 'cov_gender',
 'age_years': 'cov_age',
 'internet_time': 'cov_internet_time',
 'social_media_time': 'cov_social_media_time',
 'ai_frequency': 'cov_ai_frequency',
 'loneliness': 'cov_loneliness',
 'attention_response': 'cov_attention_response'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'ding_2026_ai_dependence': ['ai_01',
                             'ai_02',
                             'ai_03',
                             'ai_04',
                             'ai_05',
                             'ai_06',
                             'ai_07',
                             'ai_08',
                             'ai_09',
                             'ai_10',
                             'ai_11',
                             'ai_12'],
 'ding_2026_authenticity_offline': ['auth_offline_01', 'auth_offline_02', 'auth_offline_03', 'auth_offline_04'],
 'ding_2026_authenticity_online': ['auth_online_01', 'auth_online_02', 'auth_online_03', 'auth_online_04'],
 'ding_2026_who5': ['who5_01', 'who5_02', 'who5_03', 'who5_04', 'who5_05'],
 'ding_2026_mentalizing_offline': ['mental_offline_01',
                                   'mental_offline_02',
                                   'mental_offline_03',
                                   'mental_offline_04',
                                   'mental_offline_05',
                                   'mental_offline_06',
                                   'mental_offline_07',
                                   'mental_offline_08',
                                   'mental_offline_09',
                                   'mental_offline_10',
                                   'mental_offline_11',
                                   'mental_offline_12',
                                   'mental_offline_13'],
 'ding_2026_mentalizing_online': ['mental_online_01',
                                  'mental_online_02',
                                  'mental_online_03',
                                  'mental_online_04',
                                  'mental_online_05',
                                  'mental_online_06',
                                  'mental_online_07',
                                  'mental_online_08',
                                  'mental_online_09',
                                  'mental_online_10',
                                  'mental_online_11',
                                  'mental_online_12',
                                  'mental_online_13'],
 'ding_2026_phq4': ['phq4_01', 'phq4_02', 'phq4_03', 'phq4_04']}
# (lo, hi) response range per table
RANGES = {'ding_2026_ai_dependence': (1, 6),
 'ding_2026_authenticity_offline': (1, 7),
 'ding_2026_authenticity_online': (1, 7),
 'ding_2026_who5': (0, 5),
 'ding_2026_mentalizing_offline': (1, 6),
 'ding_2026_mentalizing_online': (1, 6),
 'ding_2026_phq4': (0, 3)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'who5_total': 'scale total / mean',
 'who5_score_100': 'scale total / mean',
 'gad2_total': 'scale total / mean',
 'phq2_total': 'scale total / mean',
 'phq4_total': 'scale total / mean',
 'ai_instrumental_total': 'scale total / mean',
 'ai_relational_total': 'scale total / mean',
 'ai_dependency_total': 'scale total / mean',
 'rfqy_offline_uncertainty_mean': 'scale total / mean',
 'rfqy_offline_certainty_mean': 'scale total / mean',
 'rfqy_online_uncertainty_mean': 'scale total / mean',
 'rfqy_online_certainty_mean': 'scale total / mean'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


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
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
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
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
