#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.34001004.v2
# DOI: 10.6084/m9.figshare.34001004.v2 (data)
#   Afzali H, Taheri A, Pour Seyyed Aghaei ZS (2026). Examining the Mediating Role of Body Appreciation in the Relationship Between Sexual Mindfulness and Relational Flourishing in Couples [Data set]. figshare. https://doi.org/10.6084/m9.figshare.34001004.v2
# License: CC BY 4.0 (record metadata)
# Data: hanie.sav, 607 married Iranians; id = row order. Persian variable labels name the demographics and pandare1
#   ('sexual self-concept question'); blocks read from the codes and the record (sexual mindfulness sm, body appreciation ba,
#   relational flourishing rf). All items 1-5; one ba3 cell coded 6 is set missing.
# Covariates: age band, marriage duration, number of children, education, employment (codes).
# Dropped: seven scale/subscale scores.
# PII: none.
# Item text: no item labels except pandare1; instruments not reproduced in the deposit.
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
URL = 'https://ndownloader.figshare.com/files/69358395'
N_ROWS = 607
ID_COL = None
COVS = {'sen': 'cov_age_band',
 'ezdevaj': 'cov_marriage_duration',
 'farzand': 'cov_children',
 'tahsilat': 'cov_education',
 'shoghl': 'cov_employment'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'afzali_2026_sexual_mindfulness': ['sm1',
                                    'sm2',
                                    'sm3',
                                    'sm4',
                                    'sm5',
                                    'sm6',
                                    'sm7',
                                    'sm8',
                                    'sm9',
                                    'sm10',
                                    'sm11',
                                    'sm12',
                                    'sm13',
                                    'sm14',
                                    'sm15',
                                    'sm16',
                                    'sm17',
                                    'sm18',
                                    'sm19'],
 'afzali_2026_body_appreciation': ['ba1', 'ba2', 'ba3', 'ba4', 'ba5', 'ba6', 'ba7', 'ba8', 'ba9', 'ba10'],
 'afzali_2026_relational_flourishing': ['rf1',
                                        'rf2',
                                        'rf3',
                                        'rf4',
                                        'rf5',
                                        'rf6',
                                        'rf7',
                                        'rf8',
                                        'rf9',
                                        'rf10',
                                        'rf11',
                                        'rf12'],
 'afzali_2026_sexual_self_concept': ['pandare1',
                                     'pandare2',
                                     'pandare3',
                                     'pandare4',
                                     'pandare5',
                                     'pandare6',
                                     'pandare7',
                                     'pandare8',
                                     'pandare9',
                                     'pandare10',
                                     'pandare11',
                                     'pandare12',
                                     'pandare13',
                                     'pandare14',
                                     'pandare15',
                                     'pandare16']}
# (lo, hi) response range per table
RANGES = {'afzali_2026_sexual_mindfulness': (1, 5),
 'afzali_2026_body_appreciation': (1, 5),
 'afzali_2026_relational_flourishing': (1, 5),
 'afzali_2026_sexual_self_concept': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {'afzali_2026_body_appreciation': [6]}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'zehn': 'scale / subscale score',
 'shekufa': 'scale / subscale score',
 'satis': 'scale / subscale score',
 'shkfa1': 'scale / subscale score',
 'mana': 'scale / subscale score',
 'roshd': 'scale / subscale score',
 'hadaf': 'scale / subscale score'}
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
