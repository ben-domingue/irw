#!/usr/bin/env python3
# Source: https://zenodo.org/records/22749662
# DOI: 10.5281/zenodo.22749662 (data)
#   Lie M, Widjaya JM, Saragih M (2026). Millennials vs Gen Z Sustainable Consumption: How Environmental Knowledge,
#   Environmental Care Attitude, Emotional Value, and Green Marketing affect Green Purchase Intention [Data set]. Zenodo.
#   The same 400-row Data sheet is also deposited as zenodo 18193377 and 18432488 (cell-for-cell identical); built
#   once, from the latest record.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Research Data (1).xlsx, sheet Data (row 1 = construct names, row 2 = codes): 400 Indonesian consumers, 200 Gen Z
#   and 200 Millennials (the "YearOfBirth" column holds the generation label; "Group" is its 1/2 code). The workbook's
#   other sheets are PLS-SEM output tables. Every item observed within 1-5.
# Tables, one per construct (item = column code): _environmental_knowledge (EK1-EK6), _emotional_value (EV1-EV3),
#   _green_marketing (GM1-GM3), _environmental_care (ECA1-ECA3), _green_purchase_intention (GPI1-GPI4).
# Covariates: cov_generation.
# Item text: not shipped -- codes only; no questionnaire in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/22749662/files/Research%20Data%20%281%29.xlsx/content'
N_ROWS = 400
ID_COL = 'RespondentID'
COVS = {'YearOfBirth': 'cov_generation'}
COV_MAPS = {'cov_generation': {'Gen Z': 'gen_z', 'Millennials': 'millennial'}}
RENAME = {}
BLOCKS = {'lie_2026_environmental_knowledge': ['EK1', 'EK2', 'EK3', 'EK4', 'EK5', 'EK6'], 'lie_2026_emotional_value': ['EV1', 'EV2', 'EV3'], 'lie_2026_green_marketing': ['GM1', 'GM2', 'GM3'], 'lie_2026_environmental_care': ['ECA1', 'ECA2', 'ECA3'], 'lie_2026_green_purchase_intention': ['GPI1', 'GPI2', 'GPI3', 'GPI4']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Data', header=1).iloc[:, :22]


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
