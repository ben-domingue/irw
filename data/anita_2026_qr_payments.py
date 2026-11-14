#!/usr/bin/env python3
# Source: https://zenodo.org/records/18657290
# DOI: 10.5281/zenodo.18657290 (data)
#   Anita TL, Putra A (2026). QR Code Payments as Phygital Marketing Touchpoints: Gendered Insights
#   into Tourist Satisfaction, Loyalty, and Revisit Intention [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Data Elda.xls, 240 tourists who paid by QR code; responses 1-5 (observed).
# Tables (item = column code): _qr_payment_experience QRP1-7, _tourist_satisfaction TS1-5,
#   _loyalty LOY1-5, _revisit_intention REV1-5. id = row order.
# Not carried: GEN (gender, coded 1/2 with no key in the deposit).
# Item text: not shipped -- codes only.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/18657290/files/Data%20Elda.xls/content'
N_ROWS = 240
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'anita_2026_qr_payment_experience': ['QRP1', 'QRP2', 'QRP3', 'QRP4', 'QRP5', 'QRP6', 'QRP7'], 'anita_2026_tourist_satisfaction': ['TS1', 'TS2', 'TS3', 'TS4', 'TS5'], 'anita_2026_loyalty': ['LOY1', 'LOY2', 'LOY3', 'LOY4', 'LOY5'], 'anita_2026_revisit_intention': ['REV1', 'REV2', 'REV3', 'REV4', 'REV5']}
LO, HI = 1, 5


def load(content):
    return pd.read_excel(io.BytesIO(content), engine='xlrd')


def main():
    r = requests.get(URL, timeout=180)
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    assert len(d) == N_ROWS, len(d)
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
