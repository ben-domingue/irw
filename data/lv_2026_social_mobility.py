#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.35019874.v2
# DOI: 10.6084/m9.figshare.35019874.v2 (data)
#   Lv M (2026). When the Ladder Looks Different, Attributions Matter: Perceived Social Mobility, Social Trust, and Sense of Gain [Data set]. figshare. https://doi.org/10.6084/m9.figshare.35019874.v2
# License: CC BY 4.0 (record metadata)
# Data: 'study 1.sav' (134, social-mobility manipulation) and 'study 2.sav' (147, mobility x attribution manipulation), Chinese adults;
#   4 social-trust items (1-7) and the 2-item manipulation check in both -> one table each with cov_study; the 15 sense-of-gain
#   items are 1-5 in study 1 but 1-7 in study 2, so one table per study.
# Covariates: study, condition, subjective status, gender, age band, household, income (codes).
# Dropped: composites and design dummies.
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
URL = 'https://ndownloader.figshare.com/files/71489656'
N_ROWS = 281
ID_COL = 'pid'
COVS = {'study': 'cov_study',
 'condition': 'cov_condition',
 'status': 'cov_subjective_status',
 'gender': 'cov_gender',
 'age': 'cov_age_band',
 'household': 'cov_household',
 'income': 'cov_income'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'lv_2026_sense_of_gain_s1': ['gain1.1',
                              'gain1.2',
                              'gain1.3',
                              'gain1.4',
                              'gain1.5',
                              'gain1.6',
                              'gain1.7',
                              'gain1.8',
                              'gain1.9',
                              'gain1.10',
                              'gain1.11',
                              'gain1.12',
                              'gain1.13',
                              'gain1.14',
                              'gain1.15'],
 'lv_2026_sense_of_gain_s2': ['gain2.1',
                              'gain2.2',
                              'gain2.3',
                              'gain2.4',
                              'gain2.5',
                              'gain2.6',
                              'gain2.7',
                              'gain2.8',
                              'gain2.9',
                              'gain2.10',
                              'gain2.11',
                              'gain2.12',
                              'gain2.13',
                              'gain2.14',
                              'gain2.15'],
 'lv_2026_social_trust': ['trust1', 'trust2', 'trust3', 'trust4'],
 'lv_2026_mobility_check': ['Q1_1', 'Q1_2']}
# (lo, hi) response range per table
RANGES = {'lv_2026_sense_of_gain_s1': (1, 5),
 'lv_2026_sense_of_gain_s2': (1, 7),
 'lv_2026_social_trust': (1, 7),
 'lv_2026_mobility_check': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'mobility': 'design dummy, manipulation code or composite',
 'X': 'design dummy, manipulation code or composite',
 'W': 'design dummy, manipulation code or composite',
 'Manipulation': 'design dummy, manipulation code or composite',
 'gain': 'design dummy, manipulation code or composite',
 'trust': 'design dummy, manipulation code or composite',
 'Q1F': 'design dummy, manipulation code or composite',
 'Q2F': 'design dummy, manipulation code or composite',
 'Xmani': 'design dummy, manipulation code or composite',
 'Lmobility': 'design dummy, manipulation code or composite',
 'Hmobility': 'design dummy, manipulation code or composite'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
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
    """study 1 (this URL) and study 2 stacked; trust1-4 and Q1_1-2 are shared, the gain items differ in scale (1-5 vs 1-7) so keep their own names"""
    import pyreadstat, tempfile
    r = requests.get('https://ndownloader.figshare.com/files/71489659', timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content); f.flush()
        e, _ = pyreadstat.read_sav(f.name)
    d = d.assign(study=1)
    d["condition"] = "s1_mobility_" + d["mobility"].astype(int).astype(str)
    e = e.assign(study=2)
    e["condition"] = "s2_x_" + e["X"].astype(int).astype(str) + "_w_" + e["W"].astype(int).astype(str)
    d = pd.concat([d, e], ignore_index=True)
    d["pid"] = ["s%d_%d" % (s, i) for i, s in enumerate(d["study"], 1)]
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
