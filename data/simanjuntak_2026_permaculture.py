#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.33026846.v4
# DOI: 10.6084/m9.figshare.33026846.v4 (data)
#   Simanjuntak S (2026). From Self to System: Educational Permaculture Zones and the Scaffolded Journey from Empathy to Civic Action in Indonesian Primary Schools [Data set]. figshare. https://doi.org/10.6084/m9.figshare.33026846.v4
# License: CC BY 4.0 (record metadata)
# Data: 'control and treatment group.xlsx', 2,447 Indonesian primary pupils (grades 1-6; treatment 1,179, control 1,268), the file's
#   StudentID; nine self-reported behaviour items before (Q1-9) and after (Q10-18) a nine-week permaculture intervention, 1-5.
# Covariates: treatment group (1 = EPZ), gender, grade.
# Dropped: school name and the school-location distances (geographic), totals/means/differences.
# PII: none.
# Item text: item topics are in the column names; wording would need the instrument (not in the deposit).
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
URL = 'https://ndownloader.figshare.com/files/66765869'
N_ROWS = 4894
ID_COL = 'StudentID'
COVS = {'Group': 'cov_treatment', 'Gender': 'cov_gender', 'Grade': 'cov_grade'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'simanjuntak_2026_waste_behavior': ['Trash_on_street_or_market_edge',
                                     'Trash_at_home',
                                     'Trash_in_ditches_or_trenches',
                                     'Trash_in_the_neighborhood',
                                     'Open_trash_burning',
                                     'Trash_hoarded_in_the_ground',
                                     'Trash_on_river_or_sea',
                                     'Conventional_plastic_from_factory',
                                     'Plastic_given_by_seller']}
# (lo, hi) response range per table
RANGES = {'simanjuntak_2026_waste_behavior': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'SchoolName': 'school name',
 'Elevation_m': 'school location: elevation / distance to a landmark (geographic)',
 'Distance_Dumpsite_m': 'school location: elevation / distance to a landmark (geographic)',
 'Distance_Open_trash_burning': 'school location: elevation / distance to a landmark (geographic)',
 'Distance_River_m': 'school location: elevation / distance to a landmark (geographic)',
 'Distance_Ditch': 'school location: elevation / distance to a landmark (geographic)',
 'Distance_Market_m': 'school location: elevation / distance to a landmark (geographic)',
 'Distance_Store': 'school location: elevation / distance to a landmark (geographic)',
 'Survey': 'total, mean, difference, filter or survey label',
 'Total_Control_Pre_Test': 'total, mean, difference, filter or survey label',
 'Total_Control_Post_Test': 'total, mean, difference, filter or survey label',
 'Mean_Pre_Test': 'total, mean, difference, filter or survey label',
 'Mean_Post_Test': 'total, mean, difference, filter or survey label',
 'Different_Pre_and_Post_Test': 'total, mean, difference, filter or survey label',
 'filter_$': 'total, mean, difference, filter or survey label'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = {'simanjuntak_2026_waste_behavior'}
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """pre-test Q1-9 and post-test Q10-18 ask the same nine items: item = the text after the question number; wave 1 = pre, 2 = post"""
    pre = [c for c in d.columns if c.startswith("Pretest_Q")]
    post = [c for c in d.columns if c.startswith("Post_test_Q")]
    a = d.drop(columns=post).rename(columns={c: "_".join(c.split("_")[2:]) for c in pre}).assign(wave=1)
    b = d.drop(columns=pre).rename(columns={c: "_".join(c.split("_")[3:]) for c in post}).assign(wave=2)
    return pd.concat([a, b], ignore_index=True)


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
