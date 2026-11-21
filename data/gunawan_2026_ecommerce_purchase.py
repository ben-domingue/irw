#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/33313800
# DOI: 10.6084/m9.figshare.33313800 (data)
#   Gunawan JA, Kaujaya W, Sebayang TE (2026). Dataset for: The Influence of Brand Image, Brand Trust, and Perceived
#   Value on Consumer Purchase Intention: A Study of Cross-Border E-Commerce Platforms in Indonesia [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: data_raw_anonymised.xlsx, sheet Data: 154 Indonesian e-commerce consumers, 15 items. The workbook's Codebook
#   sheet gives each item's construct and the scale, 1 = Strongly disagree .. 5 = Strongly agree, and the source each
#   construct was adapted from.
# Tables, one per construct (item = column code): _brand_image (BI1-BI4), _brand_trust (BT1-BT3), _perceived_value
#   (PV1-PV5), _purchase_intention (PI1-PI3). No demographics in the deposit.
# Item text: not shipped -- the codebook labels items only as "Brand Image indicator 1" etc.; no stems in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://ndownloader.figshare.com/files/67753692'
N_ROWS = 154
ID_COL = 'respondent_id'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'gunawan_2026_brand_image': ['BI1', 'BI2', 'BI3', 'BI4'], 'gunawan_2026_brand_trust': ['BT1', 'BT2', 'BT3'], 'gunawan_2026_perceived_value': ['PV1', 'PV2', 'PV3', 'PV4', 'PV5'], 'gunawan_2026_purchase_intention': ['PI1', 'PI2', 'PI3']}
LO, HI = 1, 5
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
