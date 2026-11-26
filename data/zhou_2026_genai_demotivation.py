#!/usr/bin/env python3
# Source: https://zenodo.org/records/24212117
# DOI: 10.5281/zenodo.24212117 (data)
#   Zhou W (2026). Adaptive GenAI Use Affect L2 Learning Demotivation [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24212117
# License: CC BY 4.0 (record metadata)
# Data: AD-1029.sav (no value labels), 1,029 Chinese tertiary EFL learners; id = row order. Blocks read from the codes and
#   the record (adaptive GenAI use -> boredom / anxiety -> demotivation); every item observed within 1-5.
# Covariates: gender, year, major, English grade band (codes as stored), completion time in seconds.
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
URL = 'https://zenodo.org/api/records/24212117/files/AD-1029.sav/content'
N_ROWS = 1029
ID_COL = None
COVS = {'性别': 'cov_gender',
 '年级': 'cov_year',
 '专业': 'cov_major',
 '英语成绩': 'cov_english_grade_band',
 'secs': 'cov_completion_time_s'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'zhou_2026_adaptive_genai_use': ['AD1', 'AD2', 'AD3', 'AD4', 'AD5', 'AD6', 'AD7'],
 'zhou_2026_bo': ['BO1', 'BO2', 'BO3', 'BO4', 'BO5', 'BO6'],
 'zhou_2026_an': ['AN1', 'AN2', 'AN3', 'AN4', 'AN5', 'AN6'],
 'zhou_2026_l2_demotivation': ['DEM1', 'DEM2', 'DEM3', 'DEM4', 'DEM5', 'DEM6', 'DEM7']}
# (lo, hi) response range per table
RANGES = {'zhou_2026_adaptive_genai_use': (1, 5),
 'zhou_2026_bo': (1, 5),
 'zhou_2026_an': (1, 5),
 'zhou_2026_l2_demotivation': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'序号': 'questionnaire-platform serial; 303 values repeat, so id = row order',
 '所用时间': 'carried as cov_completion_time_s',
 '总分': 'total score',
 '标准差': 'per-respondent SD of the items (screening statistic)'}
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
    d["secs"] = d["所用时间"].str.replace("秒", "").astype(int)
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
