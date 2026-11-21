#!/usr/bin/env python3
# Source: https://zenodo.org/records/20047742
# DOI: 10.5281/zenodo.20047742 (data)
#   Leo NA, Albertino B (2026). E-Wallet Continuance Intention in the Greater Jakarta Metropolitan Area (Jabodetabek),
#   Indonesia [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: "E-Wallet Continuance Intention (Responses) (1).xlsx" (the .csv in the record is the same export), 211
#   Jabodetabek e-wallet users. Row 1 of the sheet labels each block -- HABIT, PERCEIVED USEFULNESS, ECOSYSTEM
#   INTEGRATED PLATFORM, SATISFACTION, CONTINUANCE INTENTION -- and row 2 holds the Indonesian statements, five per
#   block. Every item observed within 1-5.
# Item codes: the statement headers are stems, so item = block code + position within the block (HAB1-5, PU1-5,
#   EIP1-5, SAT1-5, CI1-5), the block taken from row 1. RENAME lists the pairs. id = row order.
# Tables: _habit, _usefulness, _ecosystem_integration, _satisfaction, _continuance_intention.
# Covariates: cov_gender, cov_age_group (Gen Z / Gen Y / ... bands as recorded). Occupation, income, e-wallets used
#   and services used are not carried; the two screeners are "Ya" for everyone.
# Item text: not shipped -- the stems are in row 2, but no anchor labels in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/20047742/files/E-Wallet%20Continuance%20Intention%20%28Responses%29%20%281%29.xlsx/content'
N_ROWS = 211
ID_COL = None
COVS = {'gender': 'cov_gender', 'age': 'cov_age_group'}
COV_MAPS = {'cov_gender': {'Pria': 'male', 'Perempuan': 'female', 'Memilih untuk tidak menyebutkan': 'not_stated'}}
RENAME = {'Menggunakan e-wallet sudah menjadi bagian dari rutinitas harian saya dalam mengelola transaksi keuangan.': 'HAB1', 'Saya secara otomatis memilih e-wallet saat melakukan pembayaran digital tanpa perlu mempertimbangkan metode lain terlebih dahulu.': 'HAB2', 'E-wallet merupakan pilihan pertama yang terlintas di benak saya saat melakukan pembayaran digital.': 'HAB3', 'Saya tidak perlu berpikir panjang untuk menggunakan e-wallet saat bertransaksi digital.': 'HAB4', 'Kebiasaan saya menggunakan e-wallet tidak berubah meskipun ada perubahan situasi atau munculnya metode pembayaran baru.': 'HAB5', 'Menggunakan e-wallet membantu saya mengurangi biaya transaksi secara keseluruhan dalam aktivitas digital saya.': 'PU1', 'Ketersediaan cashback, diskon, dan promosi membuat e-wallet ini memberikan nilai finansial yang lebih baik dibandingkan metode pembayaran lainnya.': 'PU2', 'E-wallet secara efektif memenuhi kebutuhan saya dalam melakukan berbagai jenis pembayaran digital sehari-hari.': 'PU3', 'Menggunakan e-wallet membantu saya menyelesaikan berbagai transaksi digital dengan lebih mudah dan efisien dibandingkan metode pembayaran lainnya.': 'PU4', 'Menggunakan e-wallet menghemat waktu saya karena proses pembayaran menjadi lebih cepat dibandingkan metode konvensional.': 'PU5', 'E-wallet yang saya gunakan terhubung dengan berbagai layanan digital seperti e-commerce, transportasi, dan platform keuangan lainnya.': 'EIP1', 'Saya dapat menyelesaikan berbagai transaksi dalam satu e-wallet tanpa perlu berpindah aplikasi.': 'EIP2', 'E-wallet saya dapat digunakan di berbagai merchant dan platform digital tanpa hambatan teknis.': 'EIP3', 'Riwayat transaksi dan preferensi saya tersinkronisasi dengan baik di seluruh ekosistem e-wallet ini.': 'EIP4', 'Semakin banyak layanan yang terintegrasi dengan e-wallet ini, semakin besar nilai yang saya rasakan dari penggunaannya.': 'EIP5', 'Secara keseluruhan, saya puas dengan penggunaan e-wallet ini untuk transaksi digital saya.': 'SAT1', 'Semakin lama saya menggunakan e-wallet ini, semakin saya merasa puas dengan layanan yang diberikan.': 'SAT2', 'Setiap kali menggunakan e-wallet ini, saya merasakan pengalaman yang menyenangkan dan memuaskan.': 'SAT3', 'Dibandingkan dengan metode pembayaran lain yang pernah saya gunakan, e-wallet ini memberikan pengalaman yang lebih memuaskan.': 'SAT4', 'Secara keseluruhan, saya merasa bahwa pengalaman menggunakan e-wallet ini telah memenuhi harapan saya sebagai pengguna.': 'SAT5', 'Saya berniat untuk terus menggunakan e-wallet ini sebagai metode pembayaran utama saya dalam jangka panjang.': 'CI1', 'Saya akan memprioritaskan e-wallet ini dibandingkan metode pembayaran lain ketika keduanya tersedia.': 'CI2', 'Saya tidak tertarik untuk mencari alternatif pembayaran lain selama e-wallet ini memenuhi kebutuhan saya.': 'CI3', 'Saya akan merekomendasikan e-wallet ini kepada orang lain berdasarkan keseluruhan pengalaman saya menggunakannya.': 'CI4', 'Saya akan mengandalkan e-wallet ini untuk memenuhi kebutuhan transaksi digital saya di masa mendatang.': 'CI5', 'Gender': 'gender', 'Berapa umur anda?': 'age', 'Apa pekerjaan Anda saat ini?': 'occupation'}
BLOCKS = {'leo_2026_habit': ['HAB1', 'HAB2', 'HAB3', 'HAB4', 'HAB5'], 'leo_2026_usefulness': ['PU1', 'PU2', 'PU3', 'PU4', 'PU5'], 'leo_2026_ecosystem_integration': ['EIP1', 'EIP2', 'EIP3', 'EIP4', 'EIP5'], 'leo_2026_satisfaction': ['SAT1', 'SAT2', 'SAT3', 'SAT4', 'SAT5'], 'leo_2026_continuance_intention': ['CI1', 'CI2', 'CI3', 'CI4', 'CI5']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Form Responses 1', header=1)


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
