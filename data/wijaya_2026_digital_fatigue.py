#!/usr/bin/env python3
# Source: https://zenodo.org/records/24079553
# DOI: 10.5281/zenodo.24079553 (data)
#   Wijaya NN, Misela M, Halim COW, Alexander M, Sukmaningsih DW (2026). Digital Learning Platform Use Intensity and Hidden Digital Fatigue [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24079553
# License: CC BY 4.0 (record metadata)
# Data: one sheet, 353 Indonesian online learners, the file's No. Item codes only; every item observed within 1-5.
#   GF/VF/SF/MF/EF are read as the general, visual, social, motivational and emotional fatigue dimensions
#   (Zoom Exhaustion & Fatigue structure); IP = platform use intensity, CL = cognitive load (IRW's reading).
# Tables: one per code prefix.
# Covariates: gender, age band, education, weekly platform sessions, occupation.
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
URL = 'https://zenodo.org/api/records/24079553/files/raw%20data_digital%20learning.xlsx/content'
N_ROWS = 353
ID_COL = 'No'
COVS = {'Jenis Kelamin': 'cov_gender',
 'Usia': 'cov_age_band',
 'Pendidikan terakhir': 'cov_education',
 'Intensitas platform digital per minggu': 'cov_platform_sessions_week',
 'Pekerjaan saat ini': 'cov_occupation'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'wijaya_2026_platform_intensity': ['IP1', 'IP2', 'IP3', 'IP4'],
 'wijaya_2026_cognitive_load': ['CL1', 'CL2', 'CL3', 'CL4'],
 'wijaya_2026_general_fatigue': ['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
 'wijaya_2026_visual_fatigue': ['VF1', 'VF2', 'VF3', 'VF4', 'VF5'],
 'wijaya_2026_social_fatigue': ['SF1', 'SF2', 'SF3', 'SF4', 'SF5'],
 'wijaya_2026_motivational_fatigue': ['MF1', 'MF2', 'MF3', 'MF4', 'MF5'],
 'wijaya_2026_emotional_fatigue': ['EF1', 'EF2', 'EF3', 'EF4', 'EF5']}
# (lo, hi) response range per table
RANGES = {'wijaya_2026_platform_intensity': (1, 5),
 'wijaya_2026_cognitive_load': (1, 5),
 'wijaya_2026_general_fatigue': (1, 5),
 'wijaya_2026_visual_fatigue': (1, 5),
 'wijaya_2026_social_fatigue': (1, 5),
 'wijaya_2026_motivational_fatigue': (1, 5),
 'wijaya_2026_emotional_fatigue': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Platform digital yang digunakan': 'multi-select free text of platforms used',
 'Domisili': 'province (geographic)',
 'Universitas': 'university name, filled for 2 rows only'}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d["Jenis Kelamin"] = d["Jenis Kelamin"].map({"Perempuan": "female", "Laki-Laki": "male"})
    d["Usia"] = d["Usia"].str.replace(" Tahun", "").str.replace(" ", "")
    for c in ["Pendidikan terakhir", "Intensitas platform digital per minggu", "Pekerjaan saat ini"]:
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
        assert d[ID_COL].is_unique, "duplicate ids"
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
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
