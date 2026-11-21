#!/usr/bin/env python3
# Source: https://zenodo.org/records/15703337
# DOI: 10.5281/zenodo.15703337 (data)
#   Prihatna KA (2025). Online Shopping Platform Preferences: The Role of Product Assortment and Social Influence
#   RESPONSE DATA [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: sheet "RESPONSE DATA", 430 Indonesian Gen Z university students. 15 numbered statements answered with
#   labelled options whose text begins with the code ("1. Sangat TIDAK Setuju" .. "5. Sangat SETUJU"); resp = that
#   number. The record names five constructs: purchase intention, perceived ease of use, perceived usefulness,
#   product assortment, social influence.
# Item codes: the headers are the statements, three per construct, so item = construct + position. Checked by
#   reading: 1-3 the range of products (PA), 4-6 reviews, social features, popularity (SI), 7-9 easy to use / learn /
#   user-friendly (PEOU), 10-12 saves time, convenience, comparing (PU), 13-15 ordering, recommending, enjoying the
#   platform (PI). RENAME lists the pairs. id = row order.
# Tables: _product_assortment, _social_influence, _ease_of_use, _usefulness, _purchase_intention.
# Covariates: cov_gender, cov_age_group. University (free text), residence, internet and social-media use, favourite
#   games and platform are not carried.
# Item text: not shipped -- the stems are the headers and the anchors are the option labels; a cheap build later.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/15703337/files/Online%20Shopping%20Platform%20Preferences%20The%20Role%20of%20Product%20Assortment%20and%20Social%20Influence_RESPONSE%20DATA.xlsx/content'
N_ROWS = 430
ID_COL = None
COVS = {'Jenis kelamin': 'cov_gender', 'Usia saat ini': 'cov_age_group'}
COV_MAPS = {'cov_gender': {'Laki-laki': 'male', 'Perempuan': 'female'}}
RENAME = {'1. Rangkaian produk yang tersedia di platform pilihan saya memberikan nilai yang sepadan dengan uang yang saya keluarkan.': 'PA1', '2. Platform pilihan saya menawarkan rangkaian produk dari berbagai merek untuk saya pilih.': 'PA2', '3. Platform pilhan saya menyediakan rangkaian produk yang saya butuhkan, sehingga saya tidak perlu mencari di tempat lain.': 'PA3', '4. Saya dipengaruhi oleh ulasan online dan rekomendasi dari teman atau keluarga saat memutuskan untuk belanja di platform yang menjadi pilihan.': 'SI1', '5. Platform belanja online pilihan menyediakan fitur sosial yang memungkinkan saya untuk mencari opini dan berbagi pengalaman dengan orang lain sebelum membeli produk.': 'SI2', '6. Saya mempertimbangkan seberapa populer suatu platform belanja online di kalangan teman sebaya saat saya membuat keputusan belanja online..': 'SI3', '7. Platform belanja online pilihan saya mudah digunakan.': 'PEOU1', '8. Saya merasa mudah mempelajari cara berbelanja di platform pilihan saya.': 'PEOU2', '9. Platform belanja online plihan yang saya gunakan ramah pengguna dan mudah dinavigasi.': 'PEOU3', '10. Berbelanja online di platform pilihan saya menghemat waktu dibanding belanja di toko fisik.': 'PU1', '11. Berbelanja online di platform pilihan saya memberi kenyamanan dan menghemat waktu.': 'PU2', '12. Berbelanja online di platform pilihan memudahkan saya membandingkan harga dan menemukan penawaran.': 'PU3', '13. Kemudahan proses pemesanan di platform belanja online pilihan saya membuat saya berniat untuk membeli melalui platform tersebut.': 'PI1', '14. Saya berniat merekomendasikan platform belanja online pilihan saya kepada orang lain.': 'PI2', '15. Saya menikmati pengalaman menjelajahi dan mencari produk di platform belanja online pilihan saya, dan saya berniat untuk melakukan pembelian melalui platform tersebut di masa depan': 'PI3'}
BLOCKS = {'prihatna_2025_product_assortment': ['PA1', 'PA2', 'PA3'], 'prihatna_2025_social_influence': ['SI1', 'SI2', 'SI3'], 'prihatna_2025_ease_of_use': ['PEOU1', 'PEOU2', 'PEOU3'], 'prihatna_2025_usefulness': ['PU1', 'PU2', 'PU3'], 'prihatna_2025_purchase_intention': ['PI1', 'PI2', 'PI3']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='RESPONSE DATA')


def keep_rows(d):
    items = sum(BLOCKS.values(), [])
    for c in items:
        v = d[c].astype("string").str.strip().str.extract(r"^(\d)[.\s]", expand=False)
        assert v.notna().sum() == d[c].notna().sum(), c          # every answer starts with its number
        d[c] = pd.to_numeric(v)
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
