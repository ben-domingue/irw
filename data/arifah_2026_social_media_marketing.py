#!/usr/bin/env python3
# Source: https://zenodo.org/records/21113746
# DOI: 10.5281/zenodo.21113746 (data)
#   Arifah A, Putri F, Radinka NA (2026). The Influence of Social Media Marketing on Generation Z's Purchase Intention
#   in DKI Jakarta: The Mediating Role of Brand Awareness and Brand Trust [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Data_Siap_SmartPLS.csv (semicolon-separated), 100 Gen Z Instagram/TikTok users in Jakarta; 29 numbered
#   statements, every one observed within 1-5. Every non-item column is already a number: "Nama Lengkap" holds codes
#   1-99 (not unique, not names), gender and domicile are unlabelled codes; none is carried. id = row order.
# Item codes: the headers are the numbered Indonesian statements, so item = construct + position, by the title's
#   constructs and a reading of every stem: 1-11 social media marketing (entertainment, interaction,
#   informativeness, trendiness, customisation) -> SMM1-11; 12-17 brand awareness ("mengenali", "mengingat",
#   "familiar") -> BA1-6; 18-23 brand trust ("Saya percaya", "aman") -> BT1-6; 24-29 purchase intention ("tertarik /
#   berencana membeli") -> PI1-6. RENAME lists the pairs.
# Tables: _social_media_marketing, _brand_awareness, _brand_trust, _purchase_intention.
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
URL = 'https://zenodo.org/api/records/21113746/files/Data_Siap_SmartPLS.csv/content'
N_ROWS = 100
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {'1. Konten merek yang saya lihat di Instagram/TikTok menarik untuk dilihat.': 'SMM1', '2. Konten merek yang saya lihat di Instagram/TikTok menghibur saya.': 'SMM2', '3. Konten merek di Instagram/TikTok disajikan secara kreatif.': 'SMM3', '4. Merek aktif berinteraksi dengan pengguna melalui Instagram/TikTok.': 'SMM4', '5. Merek memberikan respons terhadap komentar atau pertanyaan pengguna.': 'SMM5', '6. Merek mendorong pengguna untuk berpartisipasi dalam kontennya.': 'SMM6', '7. Konten merek memberikan informasi produk yang jelas.': 'SMM7', '8. Merek rutin memberikan informasi terbaru melalui Instagram/TikTok.': 'SMM8', '9. Informasi yang disampaikan mudah dipahami.': 'SMM9', '10. Konten merek mengikuti tren yang sedang populer.': 'SMM10', '11. Konten merek sesuai dengan minat Generasi Z.': 'SMM11', '12. Saya dapat mengenali merek tersebut dengan mudah.': 'BA1', '13. Saya mengenali logo atau identitas visual merek tersebut.': 'BA2', '14. Saya dapat mengingat merek tersebut dengan mudah.': 'BA3', '15. Merek tersebut muncul pertama kali dalam pikiran saya ketika memikirkan kategori produknya.': 'BA4', '16. Saya merasa familiar dengan merek tersebut.': 'BA5', '17. Saya sering melihat merek tersebut di Instagram atau TikTok.': 'BA6', '18. Saya percaya bahwa merek tersebut dapat diandalkan.': 'BT1', '19. Saya percaya kualitas produk dari merek tersebut konsisten.': 'BT2', '20. Saya percaya merek tersebut memberikan informasi yang jujur.': 'BT3', '21. Saya percaya merek tersebut transparan mengenai produknya.': 'BT4', '22. Saya merasa aman menggunakan produk dari merek tersebut.': 'BT5', '23. Saya percaya merek tersebut mampu memenuhi harapan saya.': 'BT6', '24. Saya tertarik untuk membeli produk dari merek tersebut.': 'PI1', '25. Saya memiliki keinginan untuk membeli produk dari merek tersebut.': 'PI2', '26. Merek tersebut menjadi salah satu pilihan utama saya.': 'PI3', '27. Saya lebih memilih merek tersebut dibandingkan merek lain yang sejenis.': 'PI4', '28. Saya berencana membeli produk dari merek tersebut dalam waktu dekat.': 'PI5', '29. Kemungkinan saya membeli produk dari merek tersebut cukup tinggi.': 'PI6'}
BLOCKS = {'arifah_2026_social_media_marketing': ['SMM1', 'SMM2', 'SMM3', 'SMM4', 'SMM5', 'SMM6', 'SMM7', 'SMM8', 'SMM9', 'SMM10', 'SMM11'], 'arifah_2026_brand_awareness': ['BA1', 'BA2', 'BA3', 'BA4', 'BA5', 'BA6'], 'arifah_2026_brand_trust': ['BT1', 'BT2', 'BT3', 'BT4', 'BT5', 'BT6'], 'arifah_2026_purchase_intention': ['PI1', 'PI2', 'PI3', 'PI4', 'PI5', 'PI6']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_csv(io.BytesIO(content), sep=';')


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
