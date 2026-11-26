#!/usr/bin/env python3
# Source: https://zenodo.org/records/14626017
# DOI: 10.5281/zenodo.14626017 (data)
#   Utama I (2025). Domestic Tourist Dataset; Motivation, Risk Aspects, and Satisfaction [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Data.xlsx, 386 domestic tourists in Indonesia, 17 item columns and nothing else; 7-point
#   responses (observed 1-7; no codebook deposited).
# Tables, one per construct named in the record title (item = column code): _push_motivation
#   (Push1-3), _pull_motivation (Pull1-3), _perceived_risk (PR1-4), _satisfaction (Sa1-4),
#   _behavioral_intention (BI1-3; the code's reading, not documented). id = row order.
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
URL = 'https://zenodo.org/api/records/14626017/files/Data.xlsx/content'
N_ROWS = 386
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'utama_2025_push_motivation': ['Push1', 'Push2', 'Push3'], 'utama_2025_pull_motivation': ['Pull1', 'Pull2', 'Pull3'], 'utama_2025_perceived_risk': ['PR1', 'PR2', 'PR3', 'PR4'], 'utama_2025_satisfaction': ['Sa1', 'Sa2', 'Sa3', 'Sa4'], 'utama_2025_behavioral_intention': ['BI1', 'BI2', 'BI3']}
LO, HI = 1, 7


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
