#!/usr/bin/env python3
# Source: https://zenodo.org/records/20419368
# DOI: 10.5281/zenodo.20419368 (data)
#   Marveli CA, Ho SGH, Soraya LJ (2026). Anonymized Survey Dataset on Sales and Marketing Influences on Brand Trust
#   and Perception of Healthy Frozen Food Purchase Intention among Gen Z [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: hff_survey_anonymized_dataset.csv, 163 Gen Z consumers in Jakarta and Tangerang. codebook_hff_survey.pdf (in the
#   deposit) names the five constructs and gives the scale: 1 = Strongly Disagree .. 5 = Strongly Agree.
# Tables, one per construct (item = the deposit's column code, whitespace stripped): _sales_channel (SC001-SC005),
#   _marketing_communication (MC001-MC005), _brand_perception (BP001-BP005), _brand_trust (BT001-BT005),
#   _purchase_intention (PI001-PI004; the codebook's "PI004-PI005" is a typo, the file has PI001-PI004).
# Covariates: cov_age_group, cov_gender, cov_domicile (Jakarta / Tangerang, city level). Consumption frequency and
#   preferred brand are not carried.
# Item text: not shipped -- the codebook gives the anchors but only construct names for the items; no stems in the
#   deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/20419368/files/hff_survey_anonymized_dataset.csv/content'
N_ROWS = 163
ID_COL = 'Respondent ID'
COVS = {'Age\nUsia': 'cov_age_group', 'Gender': 'cov_gender', 'Domicile\nDomisili': 'cov_domicile'}
COV_MAPS = {'cov_gender': {'Female': 'female', 'Male': 'male'}}
RENAME = {}
BLOCKS = {'marveli_2026_sales_channel': ['SC001', 'SC002', 'SC003', 'SC004', 'SC005'], 'marveli_2026_marketing_communication': ['MC001', 'MC002', 'MC003', 'MC004', 'MC005'], 'marveli_2026_brand_perception': ['BP001', 'BP002', 'BP003', 'BP004', 'BP005'], 'marveli_2026_brand_trust': ['BT001', 'BT002', 'BT003', 'BT004', 'BT005'], 'marveli_2026_purchase_intention': ['PI001', 'PI002', 'PI003', 'PI004']}
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
