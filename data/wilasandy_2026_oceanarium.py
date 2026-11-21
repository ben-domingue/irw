#!/usr/bin/env python3
# Source: https://zenodo.org/records/20180227
# DOI: 10.5281/zenodo.20180227 (data)
#   Wilasandy C, Chairunnisa N, Heriyati P (2026). Modeling Revisit Intention in Experience-Based Tourism: A Behavioral
#   Perspective on Experience Quality and Service Quality [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: one workbook, 146 oceanarium visitors (Jakarta / South Tangerang), Google Forms. The record names five
#   constructs -- Experience Quality (EQ), Service Quality (SQ), Customer Satisfaction (CSAT), Perceived Value (PV),
#   Revisit Intention (RI) -- and the 25 item columns are their Indonesian statements, five per construct in that
#   order. Every item observed within 1-5.
# Item codes: the headers are full stems, so item = <construct><k> by position (EQ1..RI5). The tie was checked by
#   reading every stem: 1-5 are experience (pleasant, memorable, safe, attractions, educational); 6-10 service (staff
#   x2, facilities, efficient service, ticket price for the quality); 11-15 satisfaction ("puas", "sesuai harapan");
#   16-20 value ("sepadan", "berharga", "layak"); 21-25 revisit ("mengunjungi kembali"). RENAME lists the pairs.
# Tables, one per construct: _experience_quality, _service_quality, _satisfaction, _perceived_value,
#   _revisit_intention. No respondent id, so id = row order.
# Covariates: cov_age_group, cov_gender, cov_visit_purpose. Domicile, visit history and venue are not carried.
# Item text: not shipped -- the stems are the headers (Indonesian), but no response anchors are given in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/20180227/files/Data%20Modeling%20Revisit%20Intention%20in%20Experience%20Based%20Tourism.xlsx/content'
N_ROWS = 146
ID_COL = None
COVS = {'Usia': 'cov_age_group', 'Jenis Kelamin': 'cov_gender', 'Tujuan utama kunjungan Anda:': 'cov_visit_purpose'}
COV_MAPS = {'cov_gender': {'Perempuan': 'female', 'Laki-laki': 'male'}, 'cov_visit_purpose': {'Rekreasi': 'recreation', 'Edukasi': 'education', 'Konten media sosial': 'social_media_content'}}
RENAME = {'Kunjungan saya ke oceanarium merupakan pengalaman yang menyenangkan.': 'EQ1', 'Kunjungan itu menjadi pengalaman yang tak terlupakan bagi saya.': 'EQ2', 'Saya merasa nyaman dan aman saat mengunjungi oceanarium.': 'EQ3', 'Atraksi dan pertunjukannya sangat menarik dan menghibur.': 'EQ4', 'Kunjungan tersebut memberi saya pengalaman yang beredukasi.': 'EQ5', 'Para staf memberikan layanan yang profesional.': 'SQ1', 'Para staf berhasil menjawab pertanyaan-pertanyaan saya dengan baik.': 'SQ2', 'Fasilitasnya bersih dan terawat dengan baik.': 'SQ3', 'Oceanarium ini memiliki sistem layanan yang efisien.': 'SQ4', 'Harga tiketnya cukup masuk akal mengingat kualitas layanan yang diberikan.': 'SQ5', 'Saya puas dengan keputusan saya untuk mengunjungi oceanarium ini.': 'CSAT1', 'Kunjungan itu sesuai dengan harapan saya.': 'CSAT2', 'Saya puas dengan pengalaman saya secara keseluruhan.': 'CSAT3', 'Mengunjungi oceanarium ini adalah keputusan yang tepat.': 'CSAT4', 'Secara keseluruhan, saya puas dengan kunjungan ini.': 'CSAT5', 'Kunjungan itu sangat sepadan dengan uang yang saya keluarkan.': 'PV1', 'Pengalaman itu sepadan dengan waktu yang saya luangkan.': 'PV2', 'Oceanarium itu memberi manfaat yang sangat berharga bagi saya.': 'PV3', 'Kunjungan tersebut memberikan pengalaman yang berharga.': 'PV4', 'Secara keseluruhan, mengunjungi oceanarium sangat layak.': 'PV5', 'Saya berencana untuk mengunjungi kembali oceanarium ini di masa mendatang.': 'RI1', 'Saya ingin mengunjungi oceanarium ini lagi.': 'RI2', 'Saya akan mempertimbangkan oceanarium ini untuk kunjungan-kunjungan berikutnya.': 'RI3', 'Saya bersedia menghabiskan waktu dan uang untuk mengunjungi kembali tempat ini.': 'RI4', 'Saya kemungkinan besar akan berkunjung lagi dalam dua tahun ke depan.': 'RI5'}
BLOCKS = {'wilasandy_2026_experience_quality': ['EQ1', 'EQ2', 'EQ3', 'EQ4', 'EQ5'], 'wilasandy_2026_service_quality': ['SQ1', 'SQ2', 'SQ3', 'SQ4', 'SQ5'], 'wilasandy_2026_satisfaction': ['CSAT1', 'CSAT2', 'CSAT3', 'CSAT4', 'CSAT5'], 'wilasandy_2026_perceived_value': ['PV1', 'PV2', 'PV3', 'PV4', 'PV5'], 'wilasandy_2026_revisit_intention': ['RI1', 'RI2', 'RI3', 'RI4', 'RI5']}
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
