#!/usr/bin/env python3
# Source: https://zenodo.org/records/16736990
# DOI: 10.5281/zenodo.16736990 (data)
#   Yumna DT, Nafilah MKZ, Abigael V, Ferdianto (2025). Building Customer Loyalty in E-commerce with
#   User Experience and Interface Design [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Data Paper (RAW).xlsx, 453 active Indonesian e-commerce users (Google Forms, purposive
#   sample), DeLone & McLean model. Each header is the English statement followed by its code in
#   parentheses; item = that code. Responses 1-6 (observed; six-point scale).
# Tables: USQ system quality, UIQ information quality, SQ service quality (the record's three UI/UX
#   qualities), CS customer satisfaction, TR trust, CL customer loyalty; 5 items each. id = row order.
# Item text: not shipped -- the English statements are the headers, but the scales are adapted from
#   the e-commerce literature and not identified here.
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
URL = 'https://zenodo.org/api/records/16736990/files/Data%20Paper%20(RAW).xlsx/content'
N_ROWS = 453
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = 'HEADER_CODE'
BLOCKS = {'yumna_2025_system_quality': ['USQ1', 'USQ2', 'USQ3', 'USQ4', 'USQ5'], 'yumna_2025_information_quality': ['UIQ1', 'UIQ2', 'UIQ3', 'UIQ4', 'UIQ5'], 'yumna_2025_service_quality': ['SQ1', 'SQ2', 'SQ3', 'SQ4', 'SQ5'], 'yumna_2025_customer_satisfaction': ['CS1', 'CS2', 'CS3', 'CS4', 'CS5'], 'yumna_2025_trust': ['TR1', 'TR2', 'TR3', 'TR4', 'TR5'], 'yumna_2025_customer_loyalty': ['CL1', 'CL2', 'CL3', 'CL4', 'CL5']}
LO, HI = 1, 6


def load(content):
    return pd.read_excel(io.BytesIO(content)), {}


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
