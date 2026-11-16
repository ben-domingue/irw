#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/OCF1FA
# DOI: 10.7910/DVN/OCF1FA (data)
#   Mombeuil C (2025). Deciphering Customer Loyalty Dynamics in Retail Banking: The Interplay of
#   Service Quality, CRM, and CSR [Data set]. Harvard Dataverse.
# License: CC0 1.0 (Dataverse record)
# Data: CRM Clean dataset_May 2023.sav (Dataverse format=original; the .tab conversion drops the value
#   labels), 540 retail bank customers in Haiti (self-administered survey). Value labels: 1 Totally
#   disagree .. 5 totally agree. The file also holds composites and z-scores (not shipped).
# Tables (item = column name): CRM1-5 customer relationship management, ServQ1-5 service quality,
#   Satisfaction1-5, Loyalty1-5, CSR_Ass1-4 CSR associations. id = row order.
# Covariates (the .sav value labels, as written): cov_bank, cov_customer_tenure, cov_age_group,
#   cov_occupation, cov_gender.
# Item text: not shipped -- codes only.
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/10845083?format=original'
N_ROWS = 540
ID_COL = None
COVS = {'Bank': 'cov_bank', 'CustomerTenure': 'cov_customer_tenure', 'Age': 'cov_age_group', 'Occupation': 'cov_occupation', 'Gender': 'cov_gender'}
COV_MAPS = {'cov_bank': 'SAV', 'cov_customer_tenure': 'SAV', 'cov_age_group': 'SAV', 'cov_occupation': 'SAV', 'cov_gender': 'SAV'}
RENAME = {}
BLOCKS = {'mombeuil_2025_crm': ['CRM1', 'CRM2', 'CRM3', 'CRM4', 'CRM5'], 'mombeuil_2025_service_quality': ['ServQ1', 'ServQ2', 'ServQ3', 'ServQ4', 'ServQ5'], 'mombeuil_2025_satisfaction': ['Satisfaction1', 'Satisfaction2', 'Satisfaction3', 'Satisfaction4', 'Satisfaction5'], 'mombeuil_2025_loyalty': ['Loyalty1', 'Loyalty2', 'Loyalty3', 'Loyalty4', 'Loyalty5'], 'mombeuil_2025_csr_associations': ['CSR_Ass1', 'CSR_Ass2', 'CSR_Ass3', 'CSR_Ass4']}
LO, HI = 1, 5


def load(content):
    import tempfile
    import pyreadstat
    with tempfile.NamedTemporaryFile(suffix='.sav') as f:
        f.write(content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    return d, meta.variable_value_labels


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
