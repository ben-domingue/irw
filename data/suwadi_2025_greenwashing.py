#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/s58mtb8vtt (version 1)
# DOI: 10.17632/s58mtb8vtt (data)
#   Suwadi R, Soesilo P (2025). Perceived Greenwashing, Green Brand Image, Brand Trust, and NWOM among Indonesian Gen Z
#   Self-care Consumers (N = 189) [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: PGW_GBI_BT_NWOM_GenZ_Indonesia_Data.csv, 189 Indonesian Gen Z self-care product users; five-point Likert items
#   (record description), all observed within 1-5.
# Tables (item = column code): _website_interactivity (active control WI_AC1-4, two-way communication WI_TWC1-6,
#   synchronicity WI_SYN1-5), _greenwashing (GW1-GW5), _green_brand_image (GBI1-GBI4), _brand_trust (BT1-BT3),
#   _nwom (negative word-of-mouth intention, NWOM1-NWOM5). No demographics in the deposit.
# Item text: not shipped -- the record mentions a codebook, but the deposit holds the data CSV only.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://data.mendeley.com/public-files/datasets/s58mtb8vtt/files/321ea20d-840f-4883-b9fa-93248cf9e293/file_downloaded'
N_ROWS = 189
ID_COL = 'RespondentID'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'suwadi_2025_website_interactivity': ['WI_AC1', 'WI_AC2', 'WI_AC3', 'WI_AC4', 'WI_TWC1', 'WI_TWC2', 'WI_TWC3', 'WI_TWC4', 'WI_TWC5', 'WI_TWC6', 'WI_SYN1', 'WI_SYN2', 'WI_SYN3', 'WI_SYN4', 'WI_SYN5'], 'suwadi_2025_greenwashing': ['GW1', 'GW2', 'GW3', 'GW4', 'GW5'], 'suwadi_2025_green_brand_image': ['GBI1', 'GBI2', 'GBI3', 'GBI4'], 'suwadi_2025_brand_trust': ['BT1', 'BT2', 'BT3'], 'suwadi_2025_nwom': ['NWOM1', 'NWOM2', 'NWOM3', 'NWOM4', 'NWOM5']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_csv(io.BytesIO(content))


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
