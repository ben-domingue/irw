#!/usr/bin/env python3
# Source: https://zenodo.org/records/21054120
# DOI: 10.5281/zenodo.21054120 (data)
#   Prihatna KA (2026). Behavioral Intention in Mobile Banking and E-Wallet: An Integrated DOI-TAM Study RESPONSE DATA
#   [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: sheet "Zenodo Data", 230 Indonesian Gen Z respondents. 16 numbered statements answered with labelled options
#   beginning with the code ("1 Sangat Tidak Setuju" .. "5 Sangat Setuju"); resp = that number. The record names
#   observability, perceived usefulness, and behavioural intention for mobile-banking payment and for e-wallets.
# Item codes: the headers are the statements, so item = construct + position. Checked by reading: 1-4 seeing others
#   use it / being able to explain and communicate it (observability, OB); 5-8 efficiency, performance, speed,
#   effectiveness (PU); 9-12 intend / plan / recommend / suggest bank transfer (BIM); 13-16 the same four for
#   e-wallets (BIE). RENAME lists the pairs. id = row order.
# Tables: _observability, _usefulness, _intention_mobile_banking, _intention_ewallet.
# Covariates: cov_gender, cov_age (years, as recorded "18 tahun" etc.), cov_main_payment.
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
URL = 'https://zenodo.org/api/records/21054120/files/Behavioral%20Intention%20in%20Mobile%20Banking%20and%20E-Wallet%20An%20Integrated%20DOI%E2%80%93TAM%20Study_RESPONSE%20DATA.xlsx/content'
N_ROWS = 230
ID_COL = None
COVS = {'Jenis Kelamin Anda': 'cov_gender', 'Umur Anda saat ini': 'cov_age', 'main_method': 'cov_main_payment'}
COV_MAPS = {'cov_gender': {'Laki-laki': 'male', 'Perempuan': 'female'}, 'cov_main_payment': {'e-Wallet': 'e_wallet', 'mobile banking payment': 'mobile_banking'}}
RENAME = {'1. Saya akan mulai menggunakan pembayaran digital setelah melihat teman-teman saya menggunakannya.': 'OB1', '2. Teman-teman saya tampak tertarik dengan pembayaran digital setelah melihat saya menggunakannya.': 'OB2', '3. Saya yakin dapat menjelaskan kepada orang lain cara menggunakan pembayaran digital.': 'OB3', '4. Saya yakin dapat mengkomunikasikan manfaat menggunakan pembayaran digital kepada orang lain.': 'OB4', '5. Penggunaan pembayaran digital meningkatkan efisiensi saya.': 'PU1', '6. Penggunaan pembayaran digital meningkatkan kinerja/performa saya dalam mengelola keuangan.': 'PU2', '7. Menggunakan pembayaran digital membantu saya menyelesaikan transaksi keuangan lebih cepat.': 'PU3', '8. Menggunakan pembayaran digital meningkatkan efektivitas saya dalam mengelola keuangan.': 'PU4', '9. Saya berniat untuk menggunakan Transfer antar rekening Bank dalam beberapa bulan ke depan': 'BIM1', '10. Saya berencana menggunakan Transfer antar rekening Bank secara rutin.': 'BIM2', '11. Saya akan merekomendasikan penggunaan Transfer antar rekening Bank kepada orang lain.': 'BIM3', '12. Saya akan menyarankan orang yang saya kenal untuk menggunakan Transfer antar rekening Bank.': 'BIM4', '13. Saya berniat untuk tetap menggunakan e-Wallet (OVO, GoPay, ShopeePay, DANA, dll.) dalam beberapa bulan ke depan': 'BIE1', '14. Saya berencana menggunakan e-Wallet (OVO, GoPay, ShopeePay, DANA, dll.) secara rutin.': 'BIE2', '15. Saya akan merekomendasikan penggunaan e-Wallet (OVO, GoPay, ShopeePay, DANA, dll.) kepada orang lain.': 'BIE3', '16. Saya akan menyarankan orang yang saya kenal untuk menggunakan e-Wallet (OVO, GoPay, ShopeePay, DANA, dll.)': 'BIE4', 'Metode pembayaran digital paling utama yang biasa Anda gunakan dalam kegiatan sehari-hari': 'main_method'}
BLOCKS = {'prihatna_2026_observability': ['OB1', 'OB2', 'OB3', 'OB4'], 'prihatna_2026_usefulness': ['PU1', 'PU2', 'PU3', 'PU4'], 'prihatna_2026_intention_mobile_banking': ['BIM1', 'BIM2', 'BIM3', 'BIM4'], 'prihatna_2026_intention_ewallet': ['BIE1', 'BIE2', 'BIE3', 'BIE4']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Zenodo Data')


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
