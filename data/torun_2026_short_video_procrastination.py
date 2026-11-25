#!/usr/bin/env python3
# Source: https://zenodo.org/records/24116589
# DOI: 10.5281/zenodo.24116589 (data)
#   Torun H, Zorlu E (2026). The relationship between short-video addiction and academic procrastination: The serial mediating roles of self-control and impulsivity [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24116589
# License: CC BY 4.0 (record metadata)
# Data: Google Forms export (Turkish), 571 university students; id = row order. Headers carry each item's code and Turkish stem; responses
#   are text labels mapped in their natural order: KVB 5-point agreement, AEO 5-point 'describes me', OK 6-point 'describes me', BD 4-point
#   frequency (BIS-11, 30 items).
# Covariates: gender, year, perceived income, main short-video platform, daily short-video hours (text labels).
# Dropped: timestamp.
# PII: none.
# Item text: Turkish stems are in the column headers (cheap later build).
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
URL = 'https://zenodo.org/api/records/24116589/files/%C3%87al%C4%B1%C5%9Fma%20verileri.xlsx/content'
N_ROWS = 571
ID_COL = None
COVS = {'Cinsiyetiniz': 'cov_gender',
 'Sınıfınız': 'cov_year',
 'Gelir Algınız': 'cov_income_perception',
 'Günlük en çok hangi kısa video platformunu kullanırsınız. (Sadece bir tanesini işaretleyiniz)': 'cov_main_platform',
 'Günlük kısa video  (Instagram Reels, Youtube Shorts,  Whatsapp, Facebook Watch, Tiktok, Twitter) izleme süreniz': 'cov_daily_short_video_hours'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'torun_2026_short_video_addiction': ['KVB1',
                                      'KVB2',
                                      'KVB3',
                                      'KVB4',
                                      'KVB5',
                                      'KVB6',
                                      'KVB7',
                                      'KVB8',
                                      'KVB9',
                                      'KVB10'],
 'torun_2026_academic_procrastination': ['AEÖ1',
                                         'AEÖ2',
                                         'AEÖ3',
                                         'AEÖ4',
                                         'AEÖ5',
                                         'AEÖ6',
                                         'AEÖ7',
                                         'AEÖ8',
                                         'AEÖ9',
                                         'AEÖ10',
                                         'AEÖ11',
                                         'AEÖ12',
                                         'AEÖ13',
                                         'AEÖ14',
                                         'AEÖ15',
                                         'AEÖ16',
                                         'AEÖ17',
                                         'AEÖ18',
                                         'AEÖ19'],
 'torun_2026_ok': ['ÖK1',
                   'ÖK2',
                   'ÖK3',
                   'ÖK4',
                   'ÖK5',
                   'ÖK6',
                   'ÖK7',
                   'ÖK8',
                   'ÖK9',
                   'ÖK10',
                   'ÖK11',
                   'ÖK12',
                   'ÖK13',
                   'ÖK14',
                   'ÖK15',
                   'ÖK16'],
 'torun_2026_bis11': ['BD1',
                      'BD2',
                      'BD3',
                      'BD4',
                      'BD5',
                      'BD6',
                      'BD7',
                      'BD8',
                      'BD9',
                      'BD10',
                      'BD11',
                      'BD12',
                      'BD13',
                      'BD14',
                      'BD15',
                      'BD16',
                      'BD17',
                      'BD18',
                      'BD19',
                      'BD20',
                      'BD21',
                      'BD22',
                      'BD23',
                      'BD24',
                      'BD25',
                      'BD26',
                      'BD27',
                      'BD28',
                      'BD29',
                      'BD30']}
# (lo, hi) response range per table
RANGES = {'torun_2026_short_video_addiction': (1, 5),
 'torun_2026_academic_procrastination': (1, 5),
 'torun_2026_ok': (1, 6),
 'torun_2026_bis11': (1, 4)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Zaman damgası': 'form timestamp'}
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
    """item = the code that opens each header (KVB1. ..., AEO1. ..., OK1. ..., BD1. ...); text responses mapped per block"""
    maps = {'KVB': {'Tamamen Katılmıyorum.': 1, 'Katılmıyorum': 2, 'Kısmen Katılıyorum.': 3, 'Katılıyorum': 4, 'Tamamen Katılıyorum.': 5}, 'AEÖ': {'Beni hiç yansıtmıyor': 1, 'Beni çok az yansıtıyor': 2, 'Beni biraz yansıtıyor': 3, 'Beni çoğunlukla yansıtıyor': 4, 'Beni tamamen yansıtıyor': 5}, 'ÖK': {'Beni hiç tanımlamıyor.': 1, 'Beni çoğunlukla tanımlamıyor.': 2, 'Beni pek tanımlamıyor.': 3, 'Beni biraz tanımlıyor.': 4, 'Beni büyük ölçüde tanımlıyor.': 5, 'Beni tamamıyla tanımlıyor.': 6}, 'BD': {'Nadiren/Hiçbir zaman': 1, 'Bazen': 2, 'Sıklıkla': 3, 'Hemen herzaman/Herzaman': 4}}
    new = []
    for c in d.columns:
        m = re.match(r"([A-ZÇĞİÖŞÜ]+)([0-9]+)[.]", c)
        if m:
            code = m.group(1) + m.group(2)
            d[c] = d[c].map(lambda v: v if pd.isna(v) else maps[m.group(1)][str(v).strip()])
            new.append(code)
        else:
            new.append(c)
    d.columns = new
    for c in ["Cinsiyetiniz", "Sınıfınız", "Gelir Algınız"]:
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
