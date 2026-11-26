#!/usr/bin/env python3
# Source: https://zenodo.org/records/15698408
# DOI: 10.5281/zenodo.15698408 (data)
#   Mardiyah A, Salmavira A, Inasius F (2025). Voluntary Versus Enforced Tax Compliance: Empirical Evidence From
#   Digital-Based Freelancer Data [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Paper Final Dataset.xlsx, 408 Indonesian digital freelancers. The Slippery Slope Framework constructs, three
#   items each: trust in government (TR), perceived government power (P01-P03, the file's own codes, zero not O),
#   voluntary (VC) and enforced (EC) tax compliance; every item observed within 1-5. The "Name" column holds only
#   "Respondent 1".."Respondent 408" (checked) and is dropped; id = row order.
# Tables: _trust_government, _government_power, _voluntary_compliance, _enforced_compliance.
# Covariates: cov_gender, cov_age_group, cov_education (Compulsory / A-level / Academic), cov_income (Low/Medium/High).
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
URL = 'https://zenodo.org/api/records/15698408/files/Paper%20Final%20Dataset.xlsx/content'
N_ROWS = 408
ID_COL = None
COVS = {'Gender': 'cov_gender', 'Age': 'cov_age_group', 'Highest Level of Education': 'cov_education', 'Annual Income': 'cov_income'}
COV_MAPS = {'cov_gender': {'Male': 'male', 'Female': 'female'}}
RENAME = {}
BLOCKS = {'mardiyah_2025_trust_government': ['TR1', 'TR2', 'TR3'], 'mardiyah_2025_government_power': ['P01', 'P02', 'P03'], 'mardiyah_2025_voluntary_compliance': ['VC1', 'VC2', 'VC3'], 'mardiyah_2025_enforced_compliance': ['EC1', 'EC2', 'EC3']}
LO, HI = 1, 5
DROP_COLS = ['Name']


def load(content):
    return pd.read_excel(io.BytesIO(content))


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
