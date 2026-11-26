#!/usr/bin/env python3
# Source: https://zenodo.org/records/23909279
# DOI: 10.5281/zenodo.23909279 (data)
#   Anita TL (2026). The Mediating Role of User Experience in Technology Acceptance Beliefs and QRIS Payment Satisfaction among Mobile Coffee Customers [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23909279
# License: CC BY 4.0 (record metadata)
# Data: DATAQRIScoffee300.xlsx, sheet Responses, 300 mobile-coffee customers paying by QRIS in Jakarta; id = row order. Item codes
#   PEOU/PU/UX/PSS from the record's model; all items 1-5. Checked for the duplicated-row pattern that sank four earlier Anita T.L.
#   deposits in lane 2: no respondent repeats another's 15-item pattern.
# Covariates: last use, e-wallet, QR mode, gender, age band, education, occupation, coffee and QRIS frequency, QRIS tenure.
# Dropped: five constant screening answers, the Jakarta district (geographic).
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
URL = 'https://zenodo.org/api/records/23909279/files/DATAQRIScoffee300.xlsx/content'
N_ROWS = 300
ID_COL = None
COVS = {'T1': 'cov_last_use',
 'T3': 'cov_ewallet',
 'T4': 'cov_qr_mode',
 'D1': 'cov_gender',
 'D2': 'cov_age_band',
 'D3': 'cov_education',
 'D4': 'cov_occupation',
 'D5': 'cov_coffee_freq',
 'D6': 'cov_qris_freq',
 'D7': 'cov_qris_tenure'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'anita_2026_qris_peou': ['PEOU1', 'PEOU2', 'PEOU3', 'PEOU4'],
 'anita_2026_qris_pu': ['PU1', 'PU2', 'PU3', 'PU4'],
 'anita_2026_qris_ux': ['UX1', 'UX2', 'UX3', 'UX4'],
 'anita_2026_qris_satisfaction': ['PSS1', 'PSS2', 'PSS3']}
# (lo, hi) response range per table
RANGES = {'anita_2026_qris_peou': (1, 5),
 'anita_2026_qris_pu': (1, 5),
 'anita_2026_qris_ux': (1, 5),
 'anita_2026_qris_satisfaction': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'S0': 'screening question (all Yes)',
 'S1': 'screening question (all Yes)',
 'S2': 'screening question (all Yes)',
 'S3': 'screening question (all Yes)',
 'S4': 'screening question (all Yes)',
 'T2': 'Jakarta district of the purchase (geographic)'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Responses', header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    for c in ['T1', 'T3', 'T4', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']:
        d[c] = d[c].map(slug)
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
