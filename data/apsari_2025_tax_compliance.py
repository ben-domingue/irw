#!/usr/bin/env python3
# Source: https://zenodo.org/records/15697943
# DOI: 10.5281/zenodo.15697943 (data)
#   Apsari NS, Dewi RK, Lindrianasari (2025). Generation Z and Tax Compliance: Insights into Knowledge, Sanctions, and
#   Technology Adoption with Risk Preferences as a Moderating Variable [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Data Responden.xlsx, 219 Gen Z taxpayers who file their own annual return (the form's screener). The Google
#   Forms print-out in the deposit (PERTANYAAN - Google Forms.pdf) gives the scale, 1 = Sangat Tidak Setuju ..
#   5 = Sangat Setuju, and the sections: tax compliance (TC), tax knowledge (TK), tax sanctions (TS), technology
#   adoption (TA), risk preference (RP). The "Nama" column holds only "Respondent 1".."Respondent 219" (checked) and
#   is dropped; id = row order.
# Tables, one per construct (item = column code): _tax_compliance (TC1-5), _tax_knowledge (TK1-6), _tax_sanctions
#   (TS1-5), _technology_adoption (TA1-5), _risk_preference (RP1-5). No demographics in the data file.
# Item text: not shipped -- the form PDF has every Indonesian stem and the 1-5 anchors; a cheap build later, once the
#   stems are checked against the codes.
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
URL = 'https://zenodo.org/api/records/15697943/files/Data%20Responden.xlsx/content'
N_ROWS = 219
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'apsari_2025_tax_compliance': ['TC1', 'TC2', 'TC3', 'TC4', 'TC5'], 'apsari_2025_tax_knowledge': ['TK1', 'TK2', 'TK3', 'TK4', 'TK5', 'TK6'], 'apsari_2025_tax_sanctions': ['TS1', 'TS2', 'TS3', 'TS4', 'TS5'], 'apsari_2025_technology_adoption': ['TA1', 'TA2', 'TA3', 'TA4', 'TA5'], 'apsari_2025_risk_preference': ['RP1', 'RP2', 'RP3', 'RP4', 'RP5']}
LO, HI = 1, 5
DROP_COLS = ['Nama']


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
