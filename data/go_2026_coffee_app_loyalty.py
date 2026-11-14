#!/usr/bin/env python3
# Source: https://zenodo.org/records/20390216
# DOI: 10.5281/zenodo.20390216 (data)
#   Go MM, Wirawan R (2026). PLS-SEM Survey Dataset Examining the Relationship between Digital
#   Quality, Continuance Intention and Customer Loyalty [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: one CSV, 238 Generation Z users of coffee-shop mobile apps in Central Java; responses 1-4
#   (observed; four-point scale).
# Tables (item = column code): IQ1-6, SR1-6, RA1-6, SAT1-5, CIU1-5, LOY1-5. Construct names are IRW's
#   reading of the codes (information quality, system reliability, reward attractiveness,
#   satisfaction, continuance intention to use, loyalty). id = row order.
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
URL = 'https://zenodo.org/api/records/20390216/files/Anonymized%20PLS-SEM%20Survey%20Dataset%20The%20Influence%20of%20Digital%20Quality%20on%20Customer%20Loyalty%20in%20Coffee%20Shop%20Mobile%20Applications.csv/content'
N_ROWS = 238
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'go_2026_information_quality': ['IQ1', 'IQ2', 'IQ3', 'IQ4', 'IQ5', 'IQ6'], 'go_2026_system_reliability': ['SR1', 'SR2', 'SR3', 'SR4', 'SR5', 'SR6'], 'go_2026_reward_attractiveness': ['RA1', 'RA2', 'RA3', 'RA4', 'RA5', 'RA6'], 'go_2026_satisfaction': ['SAT1', 'SAT2', 'SAT3', 'SAT4', 'SAT5'], 'go_2026_continuance_intention': ['CIU1', 'CIU2', 'CIU3', 'CIU4', 'CIU5'], 'go_2026_loyalty': ['LOY1', 'LOY2', 'LOY3', 'LOY4', 'LOY5']}
LO, HI = 1, 4


def load(content):
    return pd.read_csv(io.BytesIO(content))


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
