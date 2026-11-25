#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.35100916.v1
# DOI: 10.6084/m9.figshare.35100916.v1 (data)
#   Umoru T, Babalola SS, Omolayo BO, Atoyebi TA, Owoyemi JO, Okiri GW (2026). Survey Data on Life Satisfaction, Social Capital, and Health Challenges among Older Farmers in Dekina, Kogi State, Nigeria [Data set]. figshare. https://doi.org/10.6084/m9.figshare.35100916.v1
# License: CC BY 4.0 (record metadata)
# Data: AR_Dataset_public_coarsened.csv, the depositors' open-access file (age and farming years banded, child counts capped at 10),
#   437 adults aged 60+ in farming households, Dekina, Nigeria; id = row order. AR_Codebook.xlsx gives every item's wording and
#   scale. AR_Dataset_full.csv (exact values) is marked for restricted access in the codebook and is not used.
# One HS9 value of 0 (outside 1-5, per the codebook) set missing.
# Covariates: the 13 socio-demographic columns as coded in the public file.
# PII: none.
# Item text: English wording for all 31 items in AR_Codebook.xlsx (cheap later build); questionnaire .docx in the deposit.
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
URL = 'https://ndownloader.figshare.com/files/71814973'
N_ROWS = 437
ID_COL = None
COVS = {'Age': 'cov_age_band',
 'Sex': 'cov_sex',
 'Marital_Status': 'cov_marital_status',
 'Highest_Educational_Qualification': 'cov_education',
 'Current_Farming_status': 'cov_farming_status',
 'Years_of_Farming_Experience': 'cov_farming_years_band',
 'Approximate_farm_size': 'cov_farm_size',
 'Main_Source_of_Income': 'cov_income_source',
 'Who_Lives_With_You': 'cov_lives_with',
 'Number_of_Living_Children_grandchildren': 'cov_n_children',
 'Number_of_Living_Children_grandchildren_Outside_this_Community': 'cov_n_children_away',
 'How_often_Relatives_Living_Away_Sends_MGH': 'cov_remittances',
 'Do_you_Receive__Pension': 'cov_pension'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'umoru_2026_life_satisfaction': ['LS1', 'LS2', 'LS3', 'LS4', 'LS5'],
 'umoru_2026_social_capital': ['SC1', 'SC2', 'SC3', 'SC4', 'SC5', 'SC6', 'SC7', 'SC8', 'SC9', 'SC10'],
 'umoru_2026_health_stressors': ['HS1',
                                 'HS2',
                                 'HS3',
                                 'HS4',
                                 'HS5',
                                 'HS6',
                                 'HS7',
                                 'HS8',
                                 'HS9',
                                 'HS10',
                                 'HS11',
                                 'HS12',
                                 'HS13',
                                 'HS14',
                                 'HS15',
                                 'HS16']}
# (lo, hi) response range per table
RANGES = {'umoru_2026_life_satisfaction': (1, 5), 'umoru_2026_social_capital': (1, 5), 'umoru_2026_health_stressors': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {'umoru_2026_health_stressors': [0]}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


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
