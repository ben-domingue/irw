#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/33246027
# DOI: 10.6084/m9.figshare.33246027 (data)
#   Berlian NE (2026). Survey Data: ESG Practices, Psychological Distance, Brand Trust, and Purchase Intention among
#   PT Unilever Indonesia Tbk. Product Consumers [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: Bridging_the_Gap_ESG_Survey_Data.xlsx (sheet AMOSSesg1), 490 Indonesian consumers of Unilever products. The
#   record defines the codes: ENV1-13 environmental, SOC1-6 social and GOV1-8 governance activities, PD1-6
#   psychological distance, BT1-8 brand trust, PI1-7 purchase intention. Every item observed within 1-7 (the
#   record's "Questionnaire on ESG -48-.pdf" is the instrument). No respondent id, so id = row order.
# Tables (item = column code): _esg (the three ESG facets, 27 items), _psychological_distance, _brand_trust,
#   _purchase_intention. No demographics in the file.
# Item text: not shipped -- the questionnaire PDF has the stems; a cheap build later once matched to the codes.
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
URL = 'https://ndownloader.figshare.com/files/67523292'
N_ROWS = 490
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'berlian_2026_esg': ['ENV1', 'ENV2', 'ENV3', 'ENV4', 'ENV5', 'ENV6', 'ENV7', 'ENV8', 'ENV9', 'ENV10', 'ENV11', 'ENV12', 'ENV13', 'SOC1', 'SOC2', 'SOC3', 'SOC4', 'SOC5', 'SOC6', 'GOV1', 'GOV2', 'GOV3', 'GOV4', 'GOV5', 'GOV6', 'GOV7', 'GOV8'], 'berlian_2026_psychological_distance': ['PD1', 'PD2', 'PD3', 'PD4', 'PD5', 'PD6'], 'berlian_2026_brand_trust': ['BT1', 'BT2', 'BT3', 'BT4', 'BT5', 'BT6', 'BT7', 'BT8'], 'berlian_2026_purchase_intention': ['PI1', 'PI2', 'PI3', 'PI4', 'PI5', 'PI6', 'PI7']}
LO, HI = 1, 7
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='AMOSSesg1')


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
