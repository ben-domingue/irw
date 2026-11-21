#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/32788800
# DOI: 10.6084/m9.figshare.32788800 (data)
#   Fransisca W (2026). Research Questionnaire: How Co-Branding Strategy Increases Market Penetration (Responses)
#   [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: Google Forms export, 261 active university students (the form's screener). 25 statements answered with
#   labelled options, coded here 1 = Sangat tidak setuju (STS), 2 = Tidak setuju (TS), 3 = Ragu-ragu (RG),
#   4 = Setuju (S), 5 = Sangat setuju (SS). No respondent id, so id = row order.
# Item codes: each header ends with its code in parentheses, e.g. "... kualitas yang baik. (BE3)"; item = that code.
#   The form uses "BF" twice: BF1-5 on the first block (brand fit: "cocok", "selaras", "tepat") and again on the
#   last (brand familiarity: "mengenali", "familiar"). The second block is renamed BFAM1-5 so the codes are unique.
# Tables, one per block: _brand_fit (BF1-5), _brand_equity (BE1-5: associations, quality, reputation),
#   _brand_credibility (BC1-5), _alliance_attitude (ATBA1-5, attitude toward the brand alliance), _brand_familiarity
#   (BFAM1-5). The five are the constructs the record's description names (brand fit, brand equity, brand credibility,
#   attitude toward brand alliances, brand familiarity as moderator); it reports 250 respondents, the file holds 261.
# Covariates: cov_gender, cov_age_group. Domicile and co-branding purchase frequency not carried.
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
URL = 'https://ndownloader.figshare.com/files/68373433'
N_ROWS = 261
ID_COL = None
COVS = {'Jenis Kelamin': 'cov_gender', 'Usia': 'cov_age_group'}
COV_MAPS = {'cov_gender': {'Pria': 'male', 'Wanita': 'female'}}
RENAME = {'Menurut saya, kolaborasi antara brand biasanya punya produk yang cocok. (BF1)': 'BF1', 'Menurut saya, kolaborasi antara brand lebih baik jika citra mereka selaras. (BF2)': 'BF2', 'Menurut saya, kolaborasi antara dua brand memberikan nilai yang lebih baik karena kedua brand tersebut saling melengkapi. (BF3)': 'BF3', 'Menurut saya, kolaborasi antara dua brand terasa cocok ketika produk dari kedua brand memiliki kesesuaian yang jelas. (BF4)': 'BF4', 'Menurut saya, kolaborasi antara dua brand terasa tepat ketika kedua brand memiliki konsep atau karakter yang selaras. (BF5)': 'BF5', 'Menurut saya, produk hasil kolaborasi antara dua brand memiliki nilai merek yang lebih kuat di mata konsumen. (BE1)': 'BE1', 'Brand yang terlibat dalam kolaborasi umumnya memiliki asosiasi yang positif. (BE2)': 'BE2', 'Brand yang bekerja sama biasanya memiliki kualitas yang baik. (BE3)': 'BE3', 'Kolaborasi antara brand cenderung memiliki reputasi yang baik. (BE4)': 'BE4', 'Brand yang dinilai baik biasanya tetap menjadi pilihan meskipun ada banyak pilihan lain. (BE5)': 'BE5', 'Kolaborasi antara brand biasa dilakukan oleh merek yang kredibel dan terpercaya.  (BC1)': 'BC1', 'Brand kolaborasi biasanya memiliki keahlian pada kategori produknya. (BC2)': 'BC2', 'Menurut saya, kolaborasi antara dua brand meningkatkan kepercayaan saya terhadap produk yang ditawarkan. (BC3)': 'BC3', 'Kerja sama antara brand biasanya dilakukan oleh merek yang memiliki reputasi profesional.  (BC4)': 'BC4', 'Kolaborasi antara brand biasanya melibatkan merek yang dianggap dapat dipercaya. (BC5)': 'BC5', 'Kolaborasi antara brand biasanya terlihat sebagai bisnis yang menarik. (ATBA1)': 'ATBA1', 'Kolaborasi antara brand sebagai strategi bisnis yang menguntungkan. (ATBA2)': 'ATBA2', 'Saya minat oleh konsep kolaborasi antara brand. (ATBA3)': 'ATBA3', 'Kolaborasi ini menghasilkan hubungan antara brand yang baik.  (ATBA4)': 'ATBA4', 'Saya menyukai kolaborasi antara brand. (ATBA5)': 'ATBA5', 'Saya biasanya mudah mengenali brand yang sedang berkolaborasi. (BF1)': 'BFAM1', 'Brand yang berkolaborasi sering terlihat oleh saya sebagai kesempatan untuk membeli. (BF2)': 'BFAM2', 'Saya biasanya pernah melihat atau menggunakan produk dari merek yang berkolaborasi. (BF3)': 'BFAM3', 'Brand dalam kolaborasi biasanya terasa familiar bagi saya. (BF4)': 'BFAM4', 'Saya lebih memahami kolaborasi brand, jika pernah menggunakan produk dari salah satunya. (BF5)': 'BFAM5'}
BLOCKS = {'fransisca_2026_brand_fit': ['BF1', 'BF2', 'BF3', 'BF4', 'BF5'], 'fransisca_2026_brand_equity': ['BE1', 'BE2', 'BE3', 'BE4', 'BE5'], 'fransisca_2026_brand_credibility': ['BC1', 'BC2', 'BC3', 'BC4', 'BC5'], 'fransisca_2026_alliance_attitude': ['ATBA1', 'ATBA2', 'ATBA3', 'ATBA4', 'ATBA5'], 'fransisca_2026_brand_familiarity': ['BFAM1', 'BFAM2', 'BFAM3', 'BFAM4', 'BFAM5']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Form Responses 1')


def keep_rows(d):
    LABELS = {'Sangat tidak setuju (STS)': 1, 'Tidak setuju (TS)': 2, 'Ragu - ragu (RG)': 3, 'Setuju (S)': 4, 'Sangat setuju (SS)': 5}
    items = sum(BLOCKS.values(), [])
    for c in items:
        v = d[c].map(lambda s: s.strip() if isinstance(s, str) else s)
        assert v.dropna().isin(list(LABELS)).all(), c
        d[c] = v.map(LABELS)
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
