#!/usr/bin/env python3
# Source: https://zenodo.org/records/17168441
# DOI: 10.5281/zenodo.17168441 (data)
#   Kadi ES (2025). Questionnaire results and Results of SPSS analysis [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Questionnaire results.xlsx, sheet "Form Responses 1": 108 TikTok users aged 17+ (both screeners "Ya" for
#   everyone), 18 four-point items on local-cosmetics TikTok advertising. The record names no constructs; the
#   workbook's Sheet1 (the author's SPSS input, 100 of the respondents) lays the items out as two blocks, X.1-X.9 and
#   Y.1-Y.9, with a total for each. 99 of its 100 rows equal a form row on all 18 items with form columns 1-9 = X and
#   10-18 = Y, which fixes the split.
# Item codes: the form headers are full stems, so item = X1..X9, Y1..Y9 by position, matching Sheet1's own labels.
#   X = response to the ads (noticing, attention, enjoyment, pride, brand recall, message recall, distinctiveness);
#   Y = purchase intention (interest, intent to buy, searching, adding to cart, willingness to try / buy).
# Tables: _tiktok_ad_response (X1-X9), _purchase_intention (Y1-Y9). Every item observed within 1-4 (four-point; no
#   midpoint). No respondent id in the form export, so id = row order.
# Covariates: cov_gender. The empty duplicate "Gender .1" column is dropped.
# Item text: not shipped -- the headers are the Indonesian stems, but no response anchors in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/17168441/files/Questionnaire%20results.xlsx/content'
N_ROWS = 108
ID_COL = None
COVS = {'Gender': 'cov_gender'}
COV_MAPS = {'cov_gender': {'Perempuan': 'female', 'Laki - Laki': 'male'}}
RENAME = {'Saya memperhatikan iklan kosmetik lokal saat muncul di TikTok': 'X1', 'Iklan kosmetik lokal di TikTok menarik perhatian saya': 'X2', 'Saya fokus menonton iklan kosmetik lokal hingga selesai': 'X3', 'Saya merasa senang ketika melihat iklan kosmetik lokal di TikTok': 'X4', 'Saya merasa iklan kosmetik lokal yang saya lihat menyenangkan secara visual': 'X5', 'Ketika melihat iklan, saya merasa bangga menggunakan produk kosmetik lokal Indonesia': 'X6', 'Saya dapat Mengingat nama brand kosmetik lokal setelah melihat iklannya': 'X7', 'Saya dapat mengingat pesan utama dari iklan kosmetik lokal di TikTok': 'X8', 'Saya dapat membedakan iklan kosmetik lokal yang saya lihat dari iklan kosmetik lainnya': 'X9', 'Saya tertarik mencoba produk kosmetik lokal yang saya lihat di TikTok': 'Y1', 'Saya merasa iklan produk kosmetik lokal yang saya lihat cocok untuk saya': 'Y2', 'Saya ingin tahu lebih banyak tentang iklan produk kosmetik lokal yang saya lihat': 'Y3', 'Saya berniat membeli produk kosmetik lokal tersebut setelah melihat iklannya di TikTok': 'Y4', 'Saya mencari produk kosmetik lokal tersebut di toko atau e-commerce setelah melihat Iklannya di Tiktok': 'Y5', 'Saat melihat iklan kosmetik tersebut, saya ingin memasukkan itu kedala daftar belanja saya': 'Y6', 'Saya bersedia mencoba produk kosmetik baru hanya karena melihat iklannya di TikTok': 'Y7', 'Saya merasa tidak ragu untuk membeli produk kosmetik tersebut setelah melihat iklannya': 'Y8', 'Saya bersedia untuk membeli produk kosmetik itu meskipun saya belum pernah mencoba sebelumnya': 'Y9'}
BLOCKS = {'kadi_2025_tiktok_ad_response': ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9'], 'kadi_2025_purchase_intention': ['Y1', 'Y2', 'Y3', 'Y4', 'Y5', 'Y6', 'Y7', 'Y8', 'Y9']}
LO, HI = 1, 4
DROP_COLS = ['Gender .1']


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Form Responses 1')


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
