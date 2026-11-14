#!/usr/bin/env python3
# Source: https://zenodo.org/records/21942129
# DOI: 10.5281/zenodo.21942129 (data)
#   Raden Satria M, Rofianto W (2026). From Service Stimuli to Customer Loyalty: A
#   Stimulus-Organism-Response Perspective on MRT Jakarta Users [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: one semicolon-separated CSV, 250 MRT Jakarta users (July 2026); the record names the seven
#   constructs. Responses observed 1-6 (six-point scale; no codebook deposited).
# Tables, one per construct (item = column code): physical evidence PE1-6, other customer perception
#   OCP1-5, payment system quality PSQ1-5, personnel service PS1-5, customer experience CX1-5,
#   customer satisfaction CS1-5, customer loyalty CL1-5. id = row order.
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
URL = 'https://zenodo.org/api/records/21942129/files/DATASET_MRT%20Jakarta_Service%20Stimuli%20Customer%20Loyalty.csv/content'
N_ROWS = 250
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'radensatria_2026_physical_evidence': ['PE1', 'PE2', 'PE3', 'PE4', 'PE5', 'PE6'], 'radensatria_2026_other_customers': ['OCP1', 'OCP2', 'OCP3', 'OCP4', 'OCP5'], 'radensatria_2026_payment_system_quality': ['PSQ1', 'PSQ2', 'PSQ3', 'PSQ4', 'PSQ5'], 'radensatria_2026_personnel_service': ['PS1', 'PS2', 'PS3', 'PS4', 'PS5'], 'radensatria_2026_customer_experience': ['CX1', 'CX2', 'CX3', 'CX4', 'CX5'], 'radensatria_2026_customer_satisfaction': ['CS1', 'CS2', 'CS3', 'CS4', 'CS5'], 'radensatria_2026_customer_loyalty': ['CL1', 'CL2', 'CL3', 'CL4', 'CL5']}
LO, HI = 1, 6


def load(content):
    return pd.read_csv(io.BytesIO(content), sep=';')


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
