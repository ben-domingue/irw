#!/usr/bin/env python3
# Source: https://zenodo.org/records/16604680
# DOI: 10.5281/zenodo.16604680 (data)
#   Widjaja CA, Yatalana EO, Permadi HA, Lie Y et al. (2025). AI Service Quality and Customer Loyalty
#   in the Online Food Delivery Industry [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: one .xlsx, 400 respondents, 28 item columns; responses observed 1-6. PV4 and CL2 are absent
#   from the deposit (dropped by the depositors, presumably at the outer-loading step).
# Tables (widjaja_2025_delivery_*; item = column code), constructs read from the codes and the record title:
#   e-service quality ESQ1-5, food quality FQ1-5, perceived value PV1-3,5, customer satisfaction
#   CS1-5, customer loyalty CL1,3-5, AI service quality AISQ1-5. id = row order.
# Item text: not shipped -- codes only; the record has no description or questionnaire.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/16604680/files/Dataset%20AI%20Customer%20Loyalty%20Online%20Food%20Delivery.xlsx/content'
N_ROWS = 400
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'widjaja_2025_delivery_eservice_quality': ['ESQ1', 'ESQ2', 'ESQ3', 'ESQ4', 'ESQ5'], 'widjaja_2025_delivery_food_quality': ['FQ1', 'FQ2', 'FQ3', 'FQ4', 'FQ5'], 'widjaja_2025_delivery_perceived_value': ['PV1', 'PV2', 'PV3', 'PV5'], 'widjaja_2025_delivery_satisfaction': ['CS1', 'CS2', 'CS3', 'CS4', 'CS5'], 'widjaja_2025_delivery_loyalty': ['CL1', 'CL3', 'CL4', 'CL5'], 'widjaja_2025_delivery_ai_service_quality': ['AISQ1', 'AISQ2', 'AISQ3', 'AISQ4', 'AISQ5']}
LO, HI = 1, 6


def load(content):
    return pd.read_excel(io.BytesIO(content))


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
