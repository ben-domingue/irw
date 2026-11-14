#!/usr/bin/env python3
# Source: https://zenodo.org/records/15079893
# DOI: 10.5281/zenodo.15079893 (data)
#   Kiran Raudhah Nanda P, Rifa Zahra F, Raisa Nadhira P, Sandy S (2025). Smart Retailing Technology in FnB
#   industry: Understanding the impact on Customer Attitude and Loyalty [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Data set.csv, 283 Indonesian food-and-beverage customers using self-service kiosks / BYOD ordering;
#   responses 1-5 (observed). The record names the constructs: perceived value, ease of use, enjoyment,
#   novelty, attitude, loyalty.
# Tables (item = column code; "PV 1"/"PV 2" written PV1/PV2): PV1-5, PEOU1-4, PE1-5 (enjoyment), PN1-4
#   (novelty), ATD1-4 attitude, LO1-6 loyalty. id = row order.
# Item text: not shipped -- codes only.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/15079893/files/Data%20set.csv/content'
N_ROWS = 283
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {'PV 1': 'PV1', 'PV 2': 'PV2'}
BLOCKS = {'nanda_2025_perceived_value': ['PV1', 'PV2', 'PV3', 'PV4', 'PV5'], 'nanda_2025_perceived_ease_of_use': ['PEOU1', 'PEOU2', 'PEOU3', 'PEOU4'], 'nanda_2025_perceived_enjoyment': ['PE1', 'PE2', 'PE3', 'PE4', 'PE5'], 'nanda_2025_perceived_novelty': ['PN1', 'PN2', 'PN3', 'PN4'], 'nanda_2025_attitude': ['ATD1', 'ATD2', 'ATD3', 'ATD4'], 'nanda_2025_loyalty': ['LO1', 'LO2', 'LO3', 'LO4', 'LO5', 'LO6']}
LO, HI = 1, 5


def load(content):
    return pd.read_csv(io.BytesIO(content)), {}


def main():
    r = requests.get(URL, timeout=180)
    r.raise_for_status()
    d, labels = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    if RENAME == "HEADER_CODE":  # header = "<statement> (<code>)"; item = the code
        d = d.rename(columns={c: re.search(r"\((\w+)\)\s*$", c).group(1) for c in d.columns})
    else:
        d = d.rename(columns=RENAME)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert d[ID_COL].is_unique
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        cmap = labels[src] if COV_MAPS.get(cov) == "SAV" else COV_MAPS.get(cov)
        d[cov] = d[src].map(cmap) if cmap else d[src]
        if cmap:
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
