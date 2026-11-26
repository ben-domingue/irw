#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Streamer_Performance_Flow_Experience_and_Impulse_Buying_Behavior_among_Indonesian_Live_Commerce_Shoppers/33062237
# DOI: 10.6084/m9.figshare.33062237 (data)
#   Grace, Sebayang TE (2026). Streamer Performance, Flow Experience, and Impulse Buying Behavior among Indonesian Live
#   Commerce Shoppers [Data set]. figshare. (The first author has a single name on the record.)
# License: CC BY 4.0 (figshare record metadata)
# Data: 222 rows; 27 answered "Tidak (akhiri)" to the screener and stopped, leaving 195 live-commerce buyers (the
#   record's N). Every item is observed on 1-5, so 1-5 (five-point) is taken as the range.
# Tables, one per code prefix, item = the deposit's code. The record names streamer performance, flow experience and
#   impulse buying; the dimension names are IRW's reading of the codes: _interactivity (IT1-3), _entertainment (EN1-3),
#   _enjoyment (EJ1-5), _concentration (CC1-4), _impulse_buying (IB1-4).
# Covariates: cov_gender, cov_age_group, cov_education, cov_occupation, cov_purchase_freq (translated from Indonesian).
#   Domicile (city) dropped under the geographic rule; the free-text product category is not carried.
# PII: the "Nama" column holds only the placeholders "Responden 1".."Responden 222" (asserted), not names; dropped.
#   9 text columns screened.
# Item text: not shipped -- codes only in the deposit.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://ndownloader.figshare.com/files/66895016'
N_ROWS = 222
ID_COL = None
COVS = {'Jenis Kelamin': 'cov_gender',
 'Usia': 'cov_age_group',
 'Tingkat Pendidikan Terakhir': 'cov_education',
 'Status Pekerjaan': 'cov_occupation',
 'Seberapa sering Anda membeli produk melalui platform ini dalam 1 bulan?': 'cov_purchase_freq'}
COV_MAPS = {'cov_gender': {'Perempuan': 'female', 'Laki-laki': 'male'},
 'cov_age_group': {'18–25': '18-25', '26–30': '26-30', '31–40': '31-40', '41–50': '41-50', '>50': '50+'},
 'cov_education': {'SMA/SMK/sederajat': 'senior_high',
                   'Sarjana (S1/D4)': 'bachelor',
                   'Pascasarjana (S2/S3)': 'postgraduate',
                   'Diploma (D1–D3)': 'diploma',
                   'Smp': 'junior_high'},
 'cov_occupation': {'Pelajar/Mahasiswa': 'student',
                    'Pegawai Swasta': 'private_employee',
                    'Wiraswasta/Wirausaha': 'self_employed',
                    'Ibu Rumah Tangga': 'homemaker',
                    'Pekerja Lepas (Freelancer)': 'freelancer',
                    'Pegawai Negeri': 'civil_servant',
                    'Magang': 'intern',
                    'dosen': 'lecturer',
                    'Buruh harian lepas': 'day_labourer',
                    'Tidak bekerja': 'not_working'},
 'cov_purchase_freq': {'≤2 kali': '2_or_fewer', '3–4 kali': '3_to_4', '≥5 kali': '5_or_more'}}
RENAME = {}
BLOCKS = {'grace_2026_interactivity': ['IT1', 'IT2', 'IT3'],
 'grace_2026_entertainment': ['EN1', 'EN2', 'EN3'],
 'grace_2026_enjoyment': ['EJ1', 'EJ2', 'EJ3', 'EJ4', 'EJ5'],
 'grace_2026_concentration': ['CC1', 'CC2', 'CC3', 'CC4'],
 'grace_2026_impulse_buying': ['IB1', 'IB2', 'IB3', 'IB4']}
# (lo, hi) response range per table
RANGES = {'grace_2026_interactivity': (1, 5),
 'grace_2026_entertainment': (1, 5),
 'grace_2026_enjoyment': (1, 5),
 'grace_2026_concentration': (1, 5),
 'grace_2026_impulse_buying': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Nama': 'placeholder labels',
 'Apakah Anda pernah membeli produk melalui platform ini?': 'screener',
 'Domisili Saat Ini': 'geographic, dropped',
 'Produk apa yang biasanya Anda beli melalui platform ini?': 'free text'}


def load(content):
    return pd.read_excel(io.BytesIO(content))


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    assert (d["Nama"] == [f"Responden {i}" for i in range(1, len(d) + 1)]).all()
    d = d[d["Apakah Anda pernah membeli produk melalui platform ini?"] == "Ya"].copy()
    assert len(d) == 195 and d[[c for v in BLOCKS.values() for c in v]].notna().all().all()
    for c in ["Usia", "Tingkat Pendidikan Terakhir", "Status Pekerjaan", "Seberapa sering Anda membeli produk melalui platform ini dalam 1 bulan?"]:
        d[c] = d[c].astype("string").str.strip()
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == N_ROWS, len(d)
    d = d.rename(columns=RENAME)
    d = prep(d)
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
    covs = list(COVS.values())
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
