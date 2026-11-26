#!/usr/bin/env python3
# Source: https://zenodo.org/records/17482418
# DOI: 10.5281/zenodo.17482418 (data)
#   Setyawati I, Siwabessy A, Sriwardiningsih E (2025). Data Understanding the Impact of Privacy
#   Concerns on Customer Loyalty: The Central Role of Trust in Digital Transactions [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: one .xlsx, 416 Indonesian e-commerce users; three PLS-SEM constructs. Scale 1-5 (observed;
#   no codebook deposited).
# Tables (item = column code): _privacy_concern (SP1-SP5), _trust (TR1-TR3), _customer_loyalty (CL1-CL8).
#   id = the deposit's No (unique, with gaps).
# Not carried: CodeGndr, CodeGen, CodeEd -- numeric codes with no key in the deposit.
# Item text: not shipped -- codes only, no questionnaire in the record.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/17482418/files/Data_Understanding%20the%20Impact%20of%20Privacy%20Concerns%20on%20Customer%20Loyalty-The%20Central%20Role%20of%20Trust%20in%20Digital%20Transactions.xlsx/content'
N_ROWS = 416
ID_COL = 'No'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'setyawati_2025_privacy_concern': ['SP1', 'SP2', 'SP3', 'SP4', 'SP5'], 'setyawati_2025_trust': ['TR1', 'TR2', 'TR3'], 'setyawati_2025_customer_loyalty': ['CL1', 'CL2', 'CL3', 'CL4', 'CL5', 'CL6', 'CL7', 'CL8']}
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
