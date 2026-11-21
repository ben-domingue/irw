#!/usr/bin/env python3
# Source: https://zenodo.org/records/21953535
# DOI: 10.5281/zenodo.21953535 (data)
#   Nadira AP, Mumtaza CD, Salsabila SH, Rudy (2026). Responden Kuisioner Thesis: The Influence of Artificial
#   Intelligence (AI) Based Social Media Marketing Content on Brand Trust and Purchase Decision Among Generation Z
#   in the Fashion and Beauty Industry [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Google Forms export, 320 rows; 4 screened out at the first question leave 316 Indonesian Gen Z respondents.
#   Six constructs named on the record (AI Exposure, Attitude Toward AI, AI Accuracy Perception, Brand Trust, Flow
#   Experience, Purchase Decision), four items each. The record does not state the response scale; every item is
#   observed on 1-5 (five-point agreement), so 1-5 is taken as the range.
# Tables, one per construct (item = the code in parentheses at the start of each column header, e.g. "(AE1) Saya
#   sering melihat ..." -> AE1): _ai_exposure, _attitude_ai, _ai_accuracy, _brand_trust, _flow_experience,
#   _purchase_decision. No respondent id in the file, so id = row order.
# Covariates: cov_age_group, cov_gender, cov_education, cov_occupation. Province of residence, social-media use
#   questions and the single AI-support rating are not carried.
# PII: the optional "Nama Responden" and "Nomor Handphone" columns are empty for all 320 rows (no values to carry);
#   dropped anyway.
# Item text: not shipped -- the column headers are the Indonesian stems, but no response anchors are given anywhere in
#   the deposit, and the instruments (adapted, per the thesis) are unidentified.
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
URL = 'https://zenodo.org/api/records/21953535/files/Responden%20Kuisioner%20Thesis%20The%20Influence%20of%20Artificial%20Intelligence%20AI%20Based%20Social%20Media%20Marketing%20Content%20on%20Brand%20Trust%20and%20Purchase%20Decision%20Among%20Generation%20Z%20in%20the%20Fashion%20and%20Beauty%20Industry.xlsx/content'
N_ROWS = 320
ID_COL = None
COVS = {'Usia': 'cov_age_group', 'Jenis Kelamin': 'cov_gender', 'Pendidikan Terakhir': 'cov_education', 'Pekerjaan': 'cov_occupation'}
COV_MAPS = {'cov_gender': {'Perempuan': 'female', 'Laki - Laki': 'male'}, 'cov_education': {'SMA / SMK': 'senior_high', 'Diploma / Sarjana': 'diploma_bachelor', 'Pascasarjana': 'postgraduate', 'SMP / Sederajat': 'junior_high', 'Tidak bersekolah': 'none'}, 'cov_occupation': {'Pelajar/Mahasiswa': 'student', 'Wiraswasta': 'self_employed', 'Pegawai BUMN/BUMD/Swasta': 'employee', 'Tidak Bekerja': 'not_working', 'ASN/PNS/TNI/POLRI': 'civil_servant', 'Tenaga Pendidik': 'educator', 'Profesional (Contoh: Arsitek, Dokter, Pengacara)': 'professional'}}
RENAME = {'(AE1)   Saya sering melihat konten promosi fashion atau beauty berbasis AI saat menggunakan media sosial.  (contoh: responden sering menyaksikan konten tersebut di media sosial)': 'AE1', '(AE2)     Saya sering terpapar konten promosi fashion atau beauty berbasis AI di media sosial. (contoh: konten tersebut sering muncul di media sosial responden meskipun tidak secara aktif dicari)': 'AE2', '(AE3)    Konten promosi fashion atau beauty berbasis AI sudah menjadi hal yang umum saya temui di media sosial.': 'AE3', '(AE4)     Konten promosi fashion atau beauty berbasis AI sering muncul di feed media sosial yang saya gunakan.': 'AE4', '(ATA1)     Penggunaan AI dalam konten promosi fashion atau beauty membuat pengalaman saya saat melihat media sosial menjadi lebih menarik.': 'ATA1', '(ATA2)  Saya merasa nyaman dengan penggunaan AI dalam konten promosi produk fashion atau beauty di media sosial.': 'ATA2', '(ATA3)     Saya percaya terhadap informasi produk fashion atau beauty yang disampaikan melalui AI di media sosial': 'ATA3', '(ATA4)   AI mampu memberikan rekomendasi produk fashion atau beauty yang sesuai dengan kebutuhan saya.': 'ATA4', '(AAP1)   Rekomendasi produk fashion atau beauty dari konten promosi berbasis AI terasa akurat bagi saya. (contoh: produk yang direkomendasikan sesuai dengan deskripsi atau kebutuhan saya)': 'AAP1', '(AAP2)   Saran produk fashion atau beauty dari konten promosi berbasis AI sesuai dengan kebutuhan saya. (contoh: AI merekomendasikan skincare untuk kulit berminyak saat saya mencarinya)': 'AAP2', '(AAP3)   Informasi produk fashion atau beauty yang diberikan oleh AI sesuai dengan preferensi saya. (contoh: AI menampilkan produk dengan gaya atau warna yang saya sukai)': 'AAP3', '(AAP4)   Konten promosi berbasis AI terlihat memahami kebutuhan dan preferensi saya dalam berbelanja. (contoh: AI merekomendasikan produk yang mirip dengan produk yang pernah saya cari atau beli)': 'AAP4', '(BT1)   Saya percaya pada brand fashion atau beauty yang menggunakan AI dalam konten promosinya di media sosial.': 'BT1', '(BT2)    Brand fashion atau beauty yang menggunakan AI menawarkan produk atau layanan yang dapat diandalkan.': 'BT2', '(BT3)    Saya percaya pada rekomendasi produk yang diberikan oleh brand fashion atau beauty berbasis AI': 'BT3', '(BT4)   Saya merasa lebih yakin terhadap brand fashion atau beauty yang menggunakan teknologi AI.': 'BT4', '(FE1)   Saya menikmati melihat konten promosi fashion atau beauty di media sosial tanpa terdistraksi oleh notifikasi atau konten lain.': 'FE1', '(FE2)  Saya merasa senang saat melihat konten promosi fashion atau beauty di media sosial.': 'FE2', '(FE3)   Saya suka tidak menyadari waktu telah berlalu saat melihat konten promosi fashion atau beauty di media sosial': 'FE3', '(FE4)   Saya merasa tetap bisa berhenti melihat konten promosi fashion atau beauty di media sosial kapan saja saya mau.': 'FE4', '(PD1)     Saya membeli produk fashion atau beauty berdasarkan rekomendasi dari konten promosi berbasis AI': 'PD1', '(PD2)    Konten promosi berbasis AI mempengaruhi keputusan saya dalam membeli produk fashion atau beauty.': 'PD2', '(PD3)   Saya merasa yakin dengan keputusan pembelian setelah melihat konten promosi berbasis AI.': 'PD3', '(PD4)   Konten promosi fashion atau beauty berbasis AI di media sosial membantu saya merasa puas dalam menentukan pilihan produk': 'PD4'}
BLOCKS = {'nadira_2026_ai_exposure': ['AE1', 'AE2', 'AE3', 'AE4'], 'nadira_2026_attitude_ai': ['ATA1', 'ATA2', 'ATA3', 'ATA4'], 'nadira_2026_ai_accuracy': ['AAP1', 'AAP2', 'AAP3', 'AAP4'], 'nadira_2026_brand_trust': ['BT1', 'BT2', 'BT3', 'BT4'], 'nadira_2026_flow_experience': ['FE1', 'FE2', 'FE3', 'FE4'], 'nadira_2026_purchase_decision': ['PD1', 'PD2', 'PD3', 'PD4']}
LO, HI = 1, 5
DROP_COLS = ['Nama Responden (optional)', 'Nomor Handphone\n(Silakan isi nomor handphone Anda jika bersedia mengikuti undian doorprize. Nomor yang Anda berikan hanya akan digunakan untuk keperluan pengundian dan tidak akan disebarluaskan atau digunakan untuk kepentingan lain.)']


def load(content):
    return pd.read_excel(io.BytesIO(content))


def keep_rows(d):
    # 4 respondents who answered 'Tidak' to the screener stopped there; their item cells are empty.
    return d[d[list(RENAME.values())].notna().any(axis=1)]


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
