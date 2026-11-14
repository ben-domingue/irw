#!/usr/bin/env python3
# Source: https://zenodo.org/records/15720684
# DOI: 10.5281/zenodo.15720684 (data)
#   Widjaja C, Yatalana E, Nathanael E, Pagardin M, Anisa N (2025). Beyond Entertainment: How AI,
#   Perceived Value, and Service Quality Drive Customer Engagement and Loyalty [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: one .xlsx, 240 respondents, responses 1-5 (observed). SQ3 is absent from the deposit.
# Tables (widjaja_2025_ent_*, "ent" = entertainment; item = column code), constructs from the record title: service quality SQ1,2,4,5, perceived
#   value PV1-4, AI AI1-5, customer engagement CE1-5, customer loyalty CL1-5. id = row order.
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
URL = 'https://zenodo.org/api/records/15720684/files/Beyond%20Entertainment%20Questionnaire%20Dataset.xlsx/content'
N_ROWS = 240
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'widjaja_2025_ent_service_quality': ['SQ1', 'SQ2', 'SQ4', 'SQ5'], 'widjaja_2025_ent_perceived_value': ['PV1', 'PV2', 'PV3', 'PV4'], 'widjaja_2025_ent_ai': ['AI1', 'AI2', 'AI3', 'AI4', 'AI5'], 'widjaja_2025_ent_engagement': ['CE1', 'CE2', 'CE3', 'CE4', 'CE5'], 'widjaja_2025_ent_loyalty': ['CL1', 'CL2', 'CL3', 'CL4', 'CL5']}
LO, HI = 1, 5


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
