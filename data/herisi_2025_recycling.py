#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/29965790
# DOI: 10.6084/m9.figshare.29965790 (data)
#   Mir Salehi Herisi SR, Mohd Mahdee JB, Oh KS V, Mohd Fauzi N (2025). An Integrated Model of Consumer Recycling
#   Behavior: Insights from Protection Motivation, Construal Level, and Regulatory Focus Theories [Data set]. figshare.
#   figshare 29965250 and 29586560 carry the same Data.xlsx (same MD5); built once.
# License: CC BY 4.0 (figshare record metadata)
# Data: Data.xlsx, 508 Malaysian university students, 55 items, every one observed within 1-7. The record defines
#   every construct code and names the reversed items (PROM1, PREV2, SDE1/3/5, IMP1/3/4/5). Each of those correlates
#   positively with the rest of its scale (mean r .60-.68), so the file stores them already keyed; shipped as stored,
#   item names unchanged.
# Tables (item = column code): _promotion_focus (PROM1-5), _prevention_focus (PREV1-5), _psychological_distance
#   (construal level of the MSW-pollution threat: spatial SPAT1-3, temporal TEMP1-3, social SOCS1-3, hypothetical
#   HYP1-3), the protection-motivation appraisals _severity (SEV1-3), _vulnerability (VUL1-3), _response_efficacy
#   (RESP1-3), _self_efficacy (SELF1-3), _response_cost (COST1-4), _recycling_intention (INT1-3), and the two
#   social-desirability scales _self_deceptive_enhancement (SDE1-7) and _impression_management (IMP1-7).
# Covariates: none. gen (0/1), age and edu are unlabelled codes and are not carried.
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
URL = 'https://ndownloader.figshare.com/files/57353504'
N_ROWS = 508
ID_COL = 'ID'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'herisi_2025_promotion_focus': ['PROM1', 'PROM2', 'PROM3', 'PROM4', 'PROM5'], 'herisi_2025_prevention_focus': ['PREV1', 'PREV2', 'PREV3', 'PREV4', 'PREV5'], 'herisi_2025_psychological_distance': ['SPAT1', 'SPAT2', 'SPAT3', 'TEMP1', 'TEMP2', 'TEMP3', 'SOCS1', 'SOCS2', 'SOCS3', 'HYP1', 'HYP2', 'HYP3'], 'herisi_2025_severity': ['SEV1', 'SEV2', 'SEV3'], 'herisi_2025_vulnerability': ['VUL1', 'VUL2', 'VUL3'], 'herisi_2025_response_efficacy': ['RESP1', 'RESP2', 'RESP3'], 'herisi_2025_self_efficacy': ['SELF1', 'SELF2', 'SELF3'], 'herisi_2025_response_cost': ['COST1', 'COST2', 'COST3', 'COST4'], 'herisi_2025_recycling_intention': ['INT1', 'INT2', 'INT3'], 'herisi_2025_self_deceptive_enhancement': ['SDE1', 'SDE2', 'SDE3', 'SDE4', 'SDE5', 'SDE6', 'SDE7'], 'herisi_2025_impression_management': ['IMP1', 'IMP2', 'IMP3', 'IMP4', 'IMP5', 'IMP6', 'IMP7']}
LO, HI = 1, 7
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Data')


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
