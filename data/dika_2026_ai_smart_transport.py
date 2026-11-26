#!/usr/bin/env python3
# Source: https://zenodo.org/records/23957509
# DOI: 10.5281/zenodo.23957509 (data)
#   Dika D, Mailangkay A (2026). Understanding Technology Acceptance of Artificial Intelligence in Smart Transportation Systems Among Students [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23957509
# License: CC BY 4.0 (record metadata)
# Data: 'Data after Cleaning Revisi 5 - Dean Dika.xlsx', 303 Indonesian students; id = row order. Nine 5-item blocks, codes only;
#   responses observed 1-6 (taken as six-point; 1 and 2 used in only four cells).
# Covariates: none in the deposit.
# 13 rows repeat another row's 45-item pattern -- kept (4%).
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
URL = 'https://zenodo.org/api/records/23957509/files/Data%20after%20Cleaning%20Revisi%205%20-%20Dean%20Dika.xlsx/content'
N_ROWS = 303
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'dika_2026_ai_transport_pu': ['PU1', 'PU2', 'PU3', 'PU4', 'PU5'],
 'dika_2026_ai_transport_peou': ['PEOU1', 'PEOU2', 'PEOU3', 'PEOU4', 'PEOU5'],
 'dika_2026_ai_transport_lm': ['LM1', 'LM2', 'LM3', 'LM4', 'LM5'],
 'dika_2026_ai_transport_bi': ['BI1', 'BI2', 'BI3', 'BI4', 'BI5'],
 'dika_2026_ai_transport_au': ['AU1', 'AU2', 'AU3', 'AU4', 'AU5'],
 'dika_2026_ai_transport_pe': ['PE1', 'PE2', 'PE3', 'PE4', 'PE5'],
 'dika_2026_ai_transport_efe': ['EFE1', 'EFE2', 'EFE3', 'EFE4', 'EFE5'],
 'dika_2026_ai_transport_fc': ['FC1', 'FC2', 'FC3', 'FC4', 'FC5'],
 'dika_2026_ai_transport_tr': ['TR1', 'TR2', 'TR3', 'TR4', 'TR5']}
# (lo, hi) response range per table
RANGES = {'dika_2026_ai_transport_pu': (1, 6),
 'dika_2026_ai_transport_peou': (1, 6),
 'dika_2026_ai_transport_lm': (1, 6),
 'dika_2026_ai_transport_bi': (1, 6),
 'dika_2026_ai_transport_au': (1, 6),
 'dika_2026_ai_transport_pe': (1, 6),
 'dika_2026_ai_transport_efe': (1, 6),
 'dika_2026_ai_transport_fc': (1, 6),
 'dika_2026_ai_transport_tr': (1, 6)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}
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
