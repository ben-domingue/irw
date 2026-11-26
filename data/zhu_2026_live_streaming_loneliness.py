#!/usr/bin/env python3
# Source: https://zenodo.org/records/22186191
# DOI: 10.5281/zenodo.22186191 (data)
#   Zhu ZY, Kim HC (2026). Social Loneliness [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22186191
# License: CC BY 4.0 (record metadata)
# Data: 'Social Loneliness spss.sav', 306 respondents (Korean value labels: 1 = 아주 아주 동의하지 않다 .. 7 = 아주 아주 동의);
#   id = row order. The record has no description; item codes only. PSI, PI, LONENIESS and BRANDIMAGECON are read from the
#   codes; VI, VSC, VII, PL and PURI are kept as codes.
# Covariates: viewing time/frequency, purchase, gender, age band, education, living arrangement, Weibo use, time-use codes (labels in the .sav where present).
# Dropped: the 10-option viewing checklist, a constant screening item, FLOWW (undocumented single column).
# PII: none.
# Item text: codes only (value labels give the response options).
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
URL = 'https://zenodo.org/api/records/22186191/files/Social%20Loneliness%20spss.sav/content'
N_ROWS = 306
ID_COL = None
COVS = {'시청시간': 'cov_viewing_time',
 '매주몇번': 'cov_viewing_per_week',
 '구매여부': 'cov_purchased',
 'GENDER': 'cov_gender',
 'AGE': 'cov_age_band',
 'SCHOOL': 'cov_education',
 'LIVING': 'cov_living',
 'WEIBOUSING': 'cov_weibo_use',
 'TIMEUSING': 'cov_time_using',
 'TIME': 'cov_time'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'zhu_2026_ls_vi': ['VI11',
                    'VI12',
                    'VI13',
                    'VI14',
                    'VI15',
                    'VI16',
                    'VI21',
                    'VI22',
                    'VI23',
                    'VI31',
                    'VI32',
                    'VI33',
                    'VI34'],
 'zhu_2026_ls_vsc': ['VSC1', 'VSC2', 'VSC3', 'VSC4', 'VSC5', 'VSC6'],
 'zhu_2026_ls_vii': ['VII1', 'VII2', 'VII3', 'VII4'],
 'zhu_2026_ls_parasocial_interaction': ['PSI1', 'PSI2', 'PSI3', 'PSI4', 'PSI5'],
 'zhu_2026_ls_purchase_intention': ['PI1', 'PI2', 'PI3'],
 'zhu_2026_ls_pl': ['PL1', 'PL2', 'PL3'],
 'zhu_2026_ls_puri': ['PURI1', 'PURI2', 'PURI3', 'PURI4'],
 'zhu_2026_ls_loneliness': ['LONENIESS1',
                            'LONENIESS2',
                            'LONENIESS3',
                            'LONENIESS4',
                            'LONENIESS5',
                            'LONENIESS6',
                            'LONENIESS7',
                            'LONENIESS8'],
 'zhu_2026_ls_brand_image_congruence': ['BRANDIMAGECON1',
                                        'BRANDIMAGECON2',
                                        'BRANDIMAGECON3',
                                        'BRANDIMAGECON4',
                                        'BRANDIMAGECON5',
                                        'BRANDIMAGECON6']}
# (lo, hi) response range per table
RANGES = {'zhu_2026_ls_vi': (1, 7),
 'zhu_2026_ls_vsc': (1, 7),
 'zhu_2026_ls_vii': (1, 7),
 'zhu_2026_ls_parasocial_interaction': (1, 7),
 'zhu_2026_ls_purchase_intention': (1, 7),
 'zhu_2026_ls_pl': (1, 7),
 'zhu_2026_ls_puri': (1, 7),
 'zhu_2026_ls_loneliness': (1, 7),
 'zhu_2026_ls_brand_image_congruence': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'@21': 'multi-select checklist (binary) of what was watched',
 '@22': 'multi-select checklist (binary) of what was watched',
 '@23': 'multi-select checklist (binary) of what was watched',
 '@24': 'multi-select checklist (binary) of what was watched',
 '@25': 'multi-select checklist (binary) of what was watched',
 '@26': 'multi-select checklist (binary) of what was watched',
 '@27': 'multi-select checklist (binary) of what was watched',
 '@28': 'multi-select checklist (binary) of what was watched',
 '@29': 'multi-select checklist (binary) of what was watched',
 '@210': 'multi-select checklist (binary) of what was watched',
 '시청경험': 'screening item, constant (all 1)',
 'FLOWW': 'single unlabelled 1-6 column, meaning not documented'}
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
