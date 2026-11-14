#!/usr/bin/env python3
# Source: https://zenodo.org/records/15268013
# DOI: 10.5281/zenodo.15268013 (data)
#   Tanuwijaya BC, Antonio F, Leonardo B, Gui A, Wiryawan D, Shahudin F (2025). The Effect of
#   Security and Impact on Customer Loyalty in e-Commerce [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: SmartPLS_057IRTTEC.xlsx, 404 respondents, seven 3-item blocks, responses 1-5 (observed).
# Tables, one per block (item = column code); construct names are IRW's reading of the codes:
#   IMG brand_image, SRV service, STF satisfaction, TR trust, BHI behavioral_intention, LYT loyalty,
#   SCR security. id = row order.
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
URL = 'https://zenodo.org/api/records/15268013/files/SmartPLS_057IRTTEC.xlsx/content'
N_ROWS = 404
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'tanuwijaya_2025_brand_image': ['IMG1', 'IMG2', 'IMG3'], 'tanuwijaya_2025_service': ['SRV1', 'SRV2', 'SRV3'], 'tanuwijaya_2025_satisfaction': ['STF1', 'STF2', 'STF3'], 'tanuwijaya_2025_trust': ['TR1', 'TR2', 'TR3'], 'tanuwijaya_2025_behavioral_intention': ['BHI1', 'BHI2', 'BHI3'], 'tanuwijaya_2025_loyalty': ['LYT1', 'LYT2', 'LYT3'], 'tanuwijaya_2025_security': ['SCR1', 'SCR2', 'SCR3']}
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
