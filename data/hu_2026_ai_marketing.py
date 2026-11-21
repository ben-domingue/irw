#!/usr/bin/env python3
# Source: https://zenodo.org/records/23277953
# DOI: 10.5281/zenodo.23277953 (data)
#   Hu H-L (2026). When Trust Amplifies Attitude: AI Marketing Applications, Purchase Journey Experience and Purchase
#   Intention [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Jimmy_477_SEM.csv, 477 Taiwanese online shoppers (platforms Shopee, Momo, PChome, Yahoo). 35 items, five per
#   construct, every one observed on 1-7. The record has no description or codebook: construct names below are
#   IRW's reading of the codes against the title (AI personalised recommendation, AI personalised advertising, AI
#   customer service, purchase journey experience, attitude toward AI marketing, purchase intention, trust in AI
#   marketing), not the authors'.
# Tables (item = column code): _ai_recommendation (AIPR1-5), _ai_advertising (AIPA1-5), _ai_customer_service
#   (AICS1-5), _purchase_journey (PJE1-5), _ai_marketing_attitude (AIMA1-5), _purchase_intention (PI1-5),
#   _ai_marketing_trust (AIMT1-5). id = the file's TIME column (1..477, unique).
# Covariates: cov_platform. GENDER, AGE, EDU, OCCUP and INCOME are unkeyed numeric codes and are not carried.
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
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/23277953/files/Jimmy_477_SEM.csv/content'
N_ROWS = 477
ID_COL = 'TIME'
COVS = {'SHOPPIG': 'cov_platform'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'hu_2026_ai_recommendation': ['AIPR1', 'AIPR2', 'AIPR3', 'AIPR4', 'AIPR5'], 'hu_2026_ai_advertising': ['AIPA1', 'AIPA2', 'AIPA3', 'AIPA4', 'AIPA5'], 'hu_2026_ai_customer_service': ['AICS1', 'AICS2', 'AICS3', 'AICS4', 'AICS5'], 'hu_2026_purchase_journey': ['PJE1', 'PJE2', 'PJE3', 'PJE4', 'PJE5'], 'hu_2026_ai_marketing_attitude': ['AIMA1', 'AIMA2', 'AIMA3', 'AIMA4', 'AIMA5'], 'hu_2026_purchase_intention': ['PI1', 'PI2', 'PI3', 'PI4', 'PI5'], 'hu_2026_ai_marketing_trust': ['AIMT1', 'AIMT2', 'AIMT3', 'AIMT4', 'AIMT5']}
LO, HI = 1, 7
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
