#!/usr/bin/env python3
# Source: https://zenodo.org/records/24334802
# DOI: 10.5281/zenodo.24334802 (data)
#   Song Q, Zhang G, Wang Y (2026). Survey data on AI anthropomorphism perception in intelligent vehicle cockpits: an anonymized questionnaire dataset [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24334802
# License: CC BY 4.0 (record metadata)
# Data: sheet Data, 850 Chinese new-energy-vehicle drivers in a five-level between-subjects anthropomorphism experiment,
#   the file's ResponseID. The 'Variable Definition' sheet documents every item's construct, the 1-7 scale and PU7-9's reverse keying.
# Tables: one per construct, including the 2-item manipulation check.
# Covariates: condition, age, gender, education, NEV experience, brand, AI-use frequency, trip duration.
# Dropped: Group (copy of the condition), AgeGroup, the attention check, all composites.
# PII: none.
# Item text: the 'Variable Definition' sheet describes each item's dimension, not its wording.
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
URL = 'https://zenodo.org/api/records/24334802/files/Data%20and%20Variable%20Description.xlsx/content'
N_ROWS = 850
ID_COL = 'ResponseID'
COVS = {'Anthropomorphism_level': 'cov_condition',
 'Age': 'cov_age',
 'Gender': 'cov_gender',
 'Education': 'cov_education',
 'UsageExperience': 'cov_nev_experience',
 'Brand': 'cov_brand',
 'AIUsageFrequency': 'cov_ai_usage_freq',
 'TripDuration': 'cov_trip_duration'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'song_2026_manipulation_check': ['MC1', 'MC2'],
 'song_2026_anthropomorphism': ['AP1', 'AP2', 'AP3', 'AP4', 'AP5', 'AP6', 'AP7', 'AP8', 'AP9'],
 'song_2026_unease': ['PU1', 'PU2', 'PU3', 'PU4', 'PU5', 'PU6', 'PU7', 'PU8', 'PU9'],
 'song_2026_authenticity': ['PA1', 'PA2', 'PA3', 'PA4', 'PA5', 'PA6', 'PA7', 'PA8', 'PA9'],
 'song_2026_satisfaction': ['CS1', 'CS2', 'CS3'],
 'song_2026_trust': ['BT1', 'BT2', 'BT3', 'BT4', 'BT5', 'BT6', 'BT7', 'BT8', 'BT9'],
 'song_2026_info_willingness': ['IW1', 'IW2', 'IW3'],
 'song_2026_ai_acceptance': ['TA1', 'TA2', 'TA3']}
# (lo, hi) response range per table
RANGES = {'song_2026_manipulation_check': (1, 7),
 'song_2026_anthropomorphism': (1, 7),
 'song_2026_unease': (1, 7),
 'song_2026_authenticity': (1, 7),
 'song_2026_satisfaction': (1, 7),
 'song_2026_trust': (1, 7),
 'song_2026_info_willingness': (1, 7),
 'song_2026_ai_acceptance': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Group': 'numeric copy of Anthropomorphism_level',
 'AgeGroup': 'banded Age',
 'AC1': 'attention check (all 850 answered 7)',
 'AP': 'composite mean',
 'PU': 'composite mean',
 'PA': 'composite mean',
 'CS': 'composite mean',
 'BT': 'composite mean',
 'IW': 'composite mean',
 'MC': 'composite mean',
 'TA': 'composite mean'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Data', header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d["Gender"] = d["Gender"].map({1: "male", 2: "female"})
    d["Anthropomorphism_level"] = d["Anthropomorphism_level"].str.lower()
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
