#!/usr/bin/env python3
# Source: https://zenodo.org/records/21155959
# DOI: 10.5281/zenodo.21155959 (data)
#   Rendra AFC, Wijaya K, Azzukhruf AR, Maghribi IF (2026). Survey Dataset: The Influence of Ease of Use and Trust on
#   E-Wallet Usage Intention among University Students [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Survey_Dataset_EWallet.xlsx, 120 BINUS University (Bekasi) students. The record names three constructs on a
#   5-point Likert scale: Ease of Use (X1), Trust (X2), E-Wallet Usage Intention (Y), four items each.
# Item codes: the headers are the Indonesian statements, in construct order, so item = X1.1-X1.4, X2.1-X2.4, Y1-Y4 by
#   position. Checked by reading: 1-4 are "mudah digunakan / dipahami / praktis / tanpa kesulitan"; 5-8 begin "Saya
#   percaya" / "aman"; 9-12 are continued use, preference, intention, recommendation. RENAME lists the pairs.
# Tables: _ease_of_use, _trust, _usage_intention.
# Covariates: cov_gender, cov_semester. Preferred e-wallet, frequency of use and two yes/no questions not carried.
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
URL = 'https://zenodo.org/api/records/21155959/files/Survey_Dataset_EWallet.xlsx/content'
N_ROWS = 120
ID_COL = 'RespondenID'
COVS = {'Jenis kelamin': 'cov_gender', 'Semester': 'cov_semester'}
COV_MAPS = {'cov_gender': {'Laki-laki': 'male', 'Perempuan': 'female'}}
RENAME = {'E-wallet mudah digunakan dalam transaksi sehari-hari.': 'X1.1', 'Fitur-fitur pada e-wallet mudah dipahami': 'X1.2', 'Proses pembayaran menggunakan e-wallet terasa praktis': 'X1.3', 'Saya dapat menggunakan e-wallet tanpa kesulitan': 'X1.4', 'Saya percaya e-wallet dapat menjaga keamanan transaksi saya': 'X2.1', 'Saya merasa data pribadi saya aman saat menggunakan e-wallet': 'X2.2', 'Saya percaya saldo pada e-wallet tersimpan dengan aman': 'X2.3', 'Saya percaya e-wallet dapat digunakan dengan baik saat dibutuhkan': 'X2.4', 'Saya tertarik untuk terus menggunakan e-wallet': 'Y1', 'Saya lebih memilih pembayaran menggunakan e-wallet dibanding tunai': 'Y2', 'Saya berniat menggunakan e-wallet untuk kebutuhan sehari-hari di masa depan': 'Y3', 'Saya akan merekomendasikan penggunaan e-wallet kepada orang lain': 'Y4'}
BLOCKS = {'rendra_2026_ease_of_use': ['X1.1', 'X1.2', 'X1.3', 'X1.4'], 'rendra_2026_trust': ['X2.1', 'X2.2', 'X2.3', 'X2.4'], 'rendra_2026_usage_intention': ['Y1', 'Y2', 'Y3', 'Y4']}
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
