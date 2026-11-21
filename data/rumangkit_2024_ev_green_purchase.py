#!/usr/bin/env python3
# Source: https://zenodo.org/records/13788264
# DOI: 10.5281/zenodo.13788264 (data)
#   Rumangkit S (2024). Dataset Questionnaire Green Marketing Mix, Green Awareness, and Green Purchase [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Google Forms export, 211 Indonesian respondents on electric vehicles; 13 statements, every one observed
#   within 1-5. The record names three constructs: green marketing mix, green awareness, green purchase intention.
# Item codes: the headers are the Indonesian statements, so item = GMM1-8, GA1-2, GPI1-3 by position. Checked by
#   reading: 1-8 are the marketing mix in product / price / place / promotion pairs (appeal and reliability; purchase
#   price and running cost; charging and dealer availability; warranty and government incentives); 9-10 are
#   environmental awareness; 11-13 begin "Berminat" (interested in finding out / switching / buying). RENAME lists
#   the pairs. Note GMM3 ("the high purchase price is a consideration") is worded against the others; stored as given.
# Tables: _green_marketing_mix (GMM1-8), _green_awareness (GA1-2), _green_purchase_intention (GPI1-3).
# Covariates: cov_gender, cov_age_group (bands as recorded), cov_education. Province, occupation (free text), income
#   and prior EV awareness not carried.
# Item text: not shipped -- the stems are the headers, but no anchor labels in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/13788264/files/Dataset_Green%20Marketing%20Mix_Green%20Awarness_Green%20Purchase.xlsx/content'
N_ROWS = 211
ID_COL = None
COVS = {'Jenis Kelamin': 'cov_gender', 'Usia': 'cov_age_group', 'Tingkat pendidikan': 'cov_education'}
COV_MAPS = {'cov_gender': {'Laki - Laki': 'male', 'Perempuan': 'female'}}
RENAME = {'Kendaraan  bahan bakar listrik lebih menarik dibandingkan kendaraan bahan bakar bensin.': 'GMM1', 'Kendaraan listrik sudah bisa diandalkan untuk menjadi kendaraan utama sebagai transportasi sehari-hari.': 'GMM2', 'Tingginya harga beli kendaraan listrik menjadi sebuah pertimbangan untuk dimiliki.': 'GMM3', 'Biaya mengisi bahan bakar yang lebih murah menjadi pertimbangan memiliki kendaraan listrik.': 'GMM4', 'Fasilitas pengisian daya kendaraan listrik sudah bisa diandalkan di lingkungan tempat tinggal anda.': 'GMM5', 'Dealer dan service center kendaraan listrik  mudah ditemui di lingkungan tempat tinggal anda.': 'GMM6', 'Penawaran jaminan atau garansi kendaraan menjadi hal yang menarik untuk memiliki kendaraan listrik.': 'GMM7', 'Kebijakan serta insentif dari pemerintah dalam mendukung kendaraan listrik menjadi hal yang menarik untuk memiliki kendaraan listrik.': 'GMM8', 'Memiliki kendaraan listrik akan membantu dalam pelestarian lingkungan.': 'GA1', 'Kesadaran  akan pentingnya produk ramah lingkungan menjadi alasan membeli kendaraan listrik.': 'GA2', 'Berminat mencari tahu lebih lanjut mengenai kendaraan listrik.': 'GPI1', 'Berminat  mengganti kendaraan bahan bakar bensin konvensional dengan kendaraan listrik sebagai kendaraan utama harian.': 'GPI2', 'Berminat membeli kendaraan listrik dalam beberapa tahun kedepan.': 'GPI3'}
BLOCKS = {'rumangkit_2024_green_marketing_mix': ['GMM1', 'GMM2', 'GMM3', 'GMM4', 'GMM5', 'GMM6', 'GMM7', 'GMM8'], 'rumangkit_2024_green_awareness': ['GA1', 'GA2'], 'rumangkit_2024_green_purchase_intention': ['GPI1', 'GPI2', 'GPI3']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content))


def keep_rows(d):
    return d


def main():
    r = requests.get(URL, timeout=180, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    assert len(d) == N_ROWS, len(d)
    d = d.drop(columns=[c for c in DROP_COLS if c in d.columns])
    d = keep_rows(d)
    if ID_COL:
        assert d[ID_COL].is_unique
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        d[cov] = d[src].map(COV_MAPS[cov]) if cov in COV_MAPS else d[src]
        if cov in COV_MAPS:
            assert d[cov].notna().sum() == d[src].notna().sum(), cov
    covs = list(COVS.values())
    shipped = set()
    for name, items in BLOCKS.items():
        assert all(c in d for c in items), [c for c in items if c not in d]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(LO, HI).all() and (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(LO, HI + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert name not in shipped
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    used = set(sum(BLOCKS.values(), [])) | set(COVS) | {ID_COL}
    print("source columns not shipped:", [c for c in d.columns if c not in used and c != "id" and c not in covs])


if __name__ == "__main__":
    main()
