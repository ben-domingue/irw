#!/usr/bin/env python3
# Source: https://zenodo.org/records/24526546
# DOI: 10.5281/zenodo.24526546 (data)
#   Dagdelen AC, Mustafaoglu Cicek N (2026). Kisiler Arasi Duygu Duzenleme, Algilanan Sosyal Destek ve Psikolojik Iyi Olus: Veri Seti / Interpersonal Emotion Regulation, Perceived Social Support and Psychological Well-Being: Dataset [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24526546
# License: CC BY 4.0 (record metadata)
# Data: KDD_Veri_Seti_KVKK_temiz.sav, 212 Turkish adults (18-59); id = row order. Degisken_Sozlugu.xlsx documents every
#   column and the three scales (CBASD 12 items 1-7, KDD 20 items 1-5, PIOO 8 items 1-7); the .sav carries the value labels.
# Covariates: gender (1 kadin, 2 erkek), age.
# Dropped: serial number, the two diagnosis/medication screens (constant) and their emptied free-text
#   fields, totals, subscale scores, groupings and outlier diagnostics.
# PII: none (free text already removed by the depositors).
# Item text: the dictionary says item wording was left out for copyright; value labels give the response options.
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
URL = 'https://zenodo.org/api/records/24526546/files/KDD_Veri_Seti_KVKK_temiz.sav/content'
N_ROWS = 212
ID_COL = None
COVS = {'Cinsiyetiniz': 'cov_gender', 'Yaşınız': 'cov_age'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'dagdelen_2026_mspss': ['ÇASD1',
                         'ÇASD2',
                         'ÇASD3',
                         'ÇASD4',
                         'ÇASD5',
                         'ÇASD6',
                         'ÇASD7',
                         'ÇASD8',
                         'ÇASD9',
                         'ÇASD10',
                         'ÇASD11',
                         'ÇASD12'],
 'dagdelen_2026_ierq': ['KDD1',
                        'KDD2',
                        'KDD3',
                        'KDD4',
                        'KDD5',
                        'KDD6',
                        'KDD7',
                        'KDD8',
                        'KDD9',
                        'KDD10',
                        'KDD11',
                        'KDD12',
                        'KDD13',
                        'KDD14',
                        'KDD15',
                        'KDD16',
                        'KDD17',
                        'KDD18',
                        'KDD19',
                        'KDD20'],
 'dagdelen_2026_flourishing': ['PİO1', 'PİO2', 'PİO3', 'PİO4', 'PİO5', 'PİO6', 'PİO7', 'PİO8']}
# (lo, hi) response range per table
RANGES = {'dagdelen_2026_mspss': (1, 7), 'dagdelen_2026_ierq': (1, 5), 'dagdelen_2026_flourishing': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'sırano': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
           'diagnostic or grouping',
 'Herhangibirpsikiyatrikveyanörolojiktanınızvarmı': 'not shipped: identifier, exclusion screen (constant), emptied '
                                                    'free text, total/subscale score, outlier diagnostic or grouping',
 'Herhangibirpsikiyatrikveyanörolojiktanınızvarsanedir': 'not shipped: identifier, exclusion screen (constant), '
                                                         'emptied free text, total/subscale score, outlier '
                                                         'diagnostic or grouping',
 'Düzenlikullandığınızpsikiyatrikbirilaçvarmı': 'not shipped: identifier, exclusion screen (constant), emptied free '
                                                'text, total/subscale score, outlier diagnostic or grouping',
 'Düzenlikullandığınızpsikiyatrikbirilaçvarsanedir': 'not shipped: identifier, exclusion screen (constant), emptied '
                                                     'free text, total/subscale score, outlier diagnostic or '
                                                     'grouping',
 'ÇASDTOP': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
            'diagnostic or grouping',
 'KDDSMA': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
           'diagnostic or grouping',
 'KDDYT': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
          'diagnostic or grouping',
 'KDDODA': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
           'diagnostic or grouping',
 'KDDBAE': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
           'diagnostic or grouping',
 'PİOTOP': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
           'diagnostic or grouping',
 'PUANALMA': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
             'diagnostic or grouping',
 'MAH_1': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
          'diagnostic or grouping',
 'COO_1': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, outlier '
          'diagnostic or grouping',
 'KDDSMA_3GRUP': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, '
                 'outlier diagnostic or grouping',
 'KDDYT_3GRUP': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, '
                'outlier diagnostic or grouping',
 'KDDODA_3GRUP': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, '
                 'outlier diagnostic or grouping',
 'KDDBAE_3GRUP': 'not shipped: identifier, exclusion screen (constant), emptied free text, total/subscale score, '
                 'outlier diagnostic or grouping'}
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
