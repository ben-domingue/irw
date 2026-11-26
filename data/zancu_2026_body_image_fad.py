#!/usr/bin/env python3
# Source: https://zenodo.org/records/24461058
# DOI: 10.5281/zenodo.24461058 (data)
#   Zancu SA, Candel OS, Enea V, Cobzeanu A (2026). Body image disturbance, negative urgency and food and alcohol disturbance (FAD). Emotional dysregulation and body image coping strategies as mediators [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24461058
# License: CC BY 4.0 (record metadata)
# Data: one .sav, 752 Romanian adults at T1, 510 of whom returned at T2 (T2Participation). Item columns carry no
#   variable labels; value labels only on SEX (1 masculin, 2 feminin) and Occupation (0 unemployed, 1 student, 2 employee).
#   Instrument identities are read from the codes and the deposit title; ranges as observed.
# Tables: CEBRACS, DERS-18 and BICSI with wave (1 = T1, 2 = T2); negative urgency and EDE-Q body-image items at T1 only.
# Dropped: all scale/subscale scores; ID_Code (participant-generated code) replaced by row order.
# Covariates: sex, age, weight, height, BMI, occupation (numeric, labels in the .sav).
# PII: none beyond ID_Code, dropped.
# Item text: no variable labels; instruments are published third-party scales (CEBRACS, DERS-18, BICSI, UPPS-P, EDE-Q) -- register checks needed.
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
URL = 'https://zenodo.org/api/records/24461058/files/DATASET%20Article%20BID,%20NU%20-%20BICS,%20DERS%20-%20FAD.sav/content'
N_ROWS = 1262
ID_COL = 'pid'
COVS = {'SEX': 'cov_sex',
 'AGE': 'cov_age',
 'WEIGHT': 'cov_weight_kg',
 'HEIGHT': 'cov_height_m',
 'BMI': 'cov_bmi',
 'Occupation': 'cov_occupation'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'zancu_2026_cebracs': ['CEBRACS_1',
                        'CEBRACS_2',
                        'CEBRACS_3',
                        'CEBRACS_4',
                        'CEBRACS_5',
                        'CEBRACS_6',
                        'CEBRACS_7',
                        'CEBRACS_8',
                        'CEBRACS_9',
                        'CEBRACS_10',
                        'CEBRACS_11',
                        'CEBRACS_12',
                        'CEBRACS_13',
                        'CEBRACS_14',
                        'CEBRACS_15',
                        'CEBRACS_16',
                        'CEBRACS_17',
                        'CEBRACS_18',
                        'CEBRACS_19',
                        'CEBRACS_20',
                        'CEBRACS_21'],
 'zancu_2026_negative_urgency': ['Neg.Urge_1',
                                 'Neg.Urge_2',
                                 'Neg.Urge_3',
                                 'Neg.Urge_4',
                                 'Neg.Urge_5',
                                 'Neg.Urge_6',
                                 'Neg.Urge_7',
                                 'Neg.Urge_8',
                                 'Neg.Urge_9',
                                 'Neg.Urge_10',
                                 'Neg.Urge_11',
                                 'Neg.Urge_12'],
 'zancu_2026_ders18': ['DERS_1',
                       'DERS_2',
                       'DERS_3',
                       'DERS_4',
                       'DERS_5',
                       'DERS_6',
                       'DERS_7',
                       'DERS_8',
                       'DERS_9',
                       'DERS_10',
                       'DERS_11',
                       'DERS_12',
                       'DERS_13',
                       'DERS_14',
                       'DERS_15',
                       'DERS_16',
                       'DERS_17',
                       'DERS_18'],
 'zancu_2026_bicsi': ['BICSI_1',
                      'BICSI_2',
                      'BICSI_3',
                      'BICSI_4',
                      'BICSI_5',
                      'BICSI_6',
                      'BICSI_7',
                      'BICSI_8',
                      'BICSI_9',
                      'BICSI_10',
                      'BICSI_11',
                      'BICSI_12',
                      'BICSI_13',
                      'BICSI_14',
                      'BICSI_15',
                      'BICSI_16',
                      'BICSI_17',
                      'BICSI_18'],
 'zancu_2026_edeq_body_image': ['BI.EDEQ_1',
                                'BI.EDEQ_2',
                                'BI.EDEQ_3',
                                'BI.EDEQ_4',
                                'BI.EDEQ_5',
                                'BI.EDEQ_6',
                                'BI.EDEQ_7',
                                'BI.EDEQ_8',
                                'BI.EDEQ_9',
                                'BI.EDEQ_10',
                                'BI.EDEQ_11',
                                'BI.EDEQ_12']}
# (lo, hi) response range per table
RANGES = {'zancu_2026_cebracs': (1, 5),
 'zancu_2026_negative_urgency': (1, 4),
 'zancu_2026_ders18': (1, 5),
 'zancu_2026_bicsi': (1, 4),
 'zancu_2026_edeq_body_image': (0, 6)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'BID': 'scale / subscale score',
 'NU': 'scale / subscale score',
 'AFFIX_T1': 'scale / subscale score',
 'AFFIX_T2': 'scale / subscale score',
 'AV_T1': 'scale / subscale score',
 'AV_T2': 'scale / subscale score',
 'AE_T1': 'scale / subscale score',
 'AE_T2': 'scale / subscale score',
 'B_T1': 'scale / subscale score',
 'B_T2': 'scale / subscale score',
 'DE_T1': 'scale / subscale score',
 'DE_T2': 'scale / subscale score',
 'DERS_T1': 'scale / subscale score',
 'DERS_T2': 'scale / subscale score',
 'ID_Code': 'participant-generated code (replaced by row order)',
 'T2Participation': 'whether the participant returned at T2 (implied by wave)'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = {'zancu_2026_ders18', 'zancu_2026_bicsi', 'zancu_2026_cebracs'}
WAVE_BASE = 1


def load(content):
    import pyreadstat, tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(content); f.flush()
        d, _ = pyreadstat.read_sav(f.name, user_missing=False)
    return d


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """one row per participant x wave: T1 columns as they are, T2 columns (<SCALE>_T2_k) renamed to <SCALE>_k.
    ID_Code (participant-generated code) is replaced by the row order of the file."""
    T2 = {'CEBRACS_T2_1': 'CEBRACS_1', 'CEBRACS_T2_2': 'CEBRACS_2', 'CEBRACS_T2_3': 'CEBRACS_3', 'CEBRACS_T2_4': 'CEBRACS_4', 'CEBRACS_T2_5': 'CEBRACS_5', 'CEBRACS_T2_6': 'CEBRACS_6', 'CEBRACS_T2_7': 'CEBRACS_7', 'CEBRACS_T2_8': 'CEBRACS_8', 'CEBRACS_T2_9': 'CEBRACS_9', 'CEBRACS_T2_10': 'CEBRACS_10', 'CEBRACS_T2_11': 'CEBRACS_11', 'CEBRACS_T2_12': 'CEBRACS_12', 'CEBRACS_T2_13': 'CEBRACS_13', 'CEBRACS_T2_14': 'CEBRACS_14', 'CEBRACS_T2_15': 'CEBRACS_15', 'CEBRACS_T2_16': 'CEBRACS_16', 'CEBRACS_T2_17': 'CEBRACS_17', 'CEBRACS_T2_18': 'CEBRACS_18', 'CEBRACS_T2_19': 'CEBRACS_19', 'CEBRACS_T2_20': 'CEBRACS_20', 'CEBRACS_T2_21': 'CEBRACS_21', 'DERS_T2_1': 'DERS_1', 'DERS_T2_2': 'DERS_2', 'DERS_T2_3': 'DERS_3', 'DERS_T2_4': 'DERS_4', 'DERS_T2_5': 'DERS_5', 'DERS_T2_6': 'DERS_6', 'DERS_T2_7': 'DERS_7', 'DERS_T2_8': 'DERS_8', 'DERS_T2_9': 'DERS_9', 'DERS_T2_10': 'DERS_10', 'DERS_T2_11': 'DERS_11', 'DERS_T2_12': 'DERS_12', 'DERS_T2_13': 'DERS_13', 'DERS_T2_14': 'DERS_14', 'DERS_T2_15': 'DERS_15', 'DERS_T2_16': 'DERS_16', 'DERS_T2_17': 'DERS_17', 'DERS_T2_18': 'DERS_18', 'BICSI_T2_1': 'BICSI_1', 'BICSI_T2_2': 'BICSI_2', 'BICSI_T2_3': 'BICSI_3', 'BICSI_T2_4': 'BICSI_4', 'BICSI_T2_5': 'BICSI_5', 'BICSI_T2_6': 'BICSI_6', 'BICSI_T2_7': 'BICSI_7', 'BICSI_T2_8': 'BICSI_8', 'BICSI_T2_9': 'BICSI_9', 'BICSI_T2_10': 'BICSI_10', 'BICSI_T2_11': 'BICSI_11', 'BICSI_T2_12': 'BICSI_12', 'BICSI_T2_13': 'BICSI_13', 'BICSI_T2_14': 'BICSI_14', 'BICSI_T2_15': 'BICSI_15', 'BICSI_T2_16': 'BICSI_16', 'BICSI_T2_17': 'BICSI_17', 'BICSI_T2_18': 'BICSI_18'}
    d["pid"] = range(1, len(d) + 1)
    keep = ["pid", "SEX", "AGE", "WEIGHT", "HEIGHT", "BMI", "Occupation"]
    t1 = d.drop(columns=list(T2)).assign(wave=1)
    t2 = d[d["T2Participation"] == 1][keep + list(T2)].rename(columns=T2).assign(wave=2)
    assert len(t2) == 510
    return pd.concat([t1, t2], ignore_index=True)


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
