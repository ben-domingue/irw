#!/usr/bin/env python3
# Source: https://zenodo.org/records/14619280
# DOI: 10.5281/zenodo.14619280 (data)
#   Syamsuar D, Natasha A, Amanda C, Galih IPSNM (2025). The Effect of Gamification on Shopee in
#   Increasing Customer Loyalty and Purchase Intention [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: "Raw data - 407 (clean after UG).xlsx", 404 Shopee users in Greater Jakarta (411 surveyed;
#   the depositors removed unengaged responses). The record names the constructs: gamification,
#   customer loyalty, e-word-of-mouth, purchase intention, and TAM's perceived usefulness and ease of use.
# Tables (item = column code): GM1-5, CL1-5, EW1-5, PI1-5, PU1-5, PE1-5. Responses 1-6 (observed; six-point scale).
# Not carried: UG (the depositors' unengagement statistic used for the cleaning).
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
URL = 'https://zenodo.org/api/records/14619280/files/Raw%20data%20-%20407%20(clean%20after%20UG).xlsx/content'
N_ROWS = 404
ID_COL = 'ID'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'syamsuar_2025_gamification': ['GM1', 'GM2', 'GM3', 'GM4', 'GM5'], 'syamsuar_2025_customer_loyalty': ['CL1', 'CL2', 'CL3', 'CL4', 'CL5'], 'syamsuar_2025_ewom': ['EW1', 'EW2', 'EW3', 'EW4', 'EW5'], 'syamsuar_2025_purchase_intention': ['PI1', 'PI2', 'PI3', 'PI4', 'PI5'], 'syamsuar_2025_perceived_usefulness': ['PU1', 'PU2', 'PU3', 'PU4', 'PU5'], 'syamsuar_2025_perceived_ease_of_use': ['PE1', 'PE2', 'PE3', 'PE4', 'PE5']}
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
