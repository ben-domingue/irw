#!/usr/bin/env python3
# Source: https://zenodo.org/records/17951699
# DOI: 10.5281/zenodo.17951699 (data)
#   Kurniawati YE, Alvin, Nugroho ER, Kwee F (2025). The Role of Chatbot-AI and Digital Interactions on
#   E-Commerce Customer Loyalty among Generation Y [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Data Kuisioner.xlsx, 328 Generation Y e-commerce users in Greater Jakarta (all screened as
#   AI-feature users). Eight 5-item blocks, responses 1-5.
# Tables (item = column code; construct names are IRW's reading of the codes and the record's
#   description): CAI chatbot AI, DI digital interaction, PEOU perceived ease of use, PU perceived
#   usefulness, CON convenience (reading), BI behavioral intention, SAT satisfaction, CL customer loyalty.
# One cell is out of range and is dropped as a data-entry error: BI2 = 6 for one respondent (every
#   other cell in the file is 1-5).
# id: the deposit's No. Covariate: cov_gender. Domicile, birth cohort and screening answers are one
#   value for everyone and not carried; usage frequency and platform multi-select not carried.
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
URL = 'https://zenodo.org/api/records/17951699/files/Data%20Kuisioner.xlsx/content'
N_ROWS = 328
ID_COL = 'No.'
COVS = {'Jenis Kelamin': 'cov_gender'}
COV_MAPS = {'cov_gender': {'Laki-laki': 'male', 'Perempuan': 'female'}}
RENAME = {}
BLOCKS = {'kurniawati_2025_chatbot_ai': ['CAI1', 'CAI2', 'CAI3', 'CAI4', 'CAI5'], 'kurniawati_2025_digital_interaction': ['DI1', 'DI2', 'DI3', 'DI4', 'DI5'], 'kurniawati_2025_perceived_ease_of_use': ['PEOU1', 'PEOU2', 'PEOU3', 'PEOU4', 'PEOU5'], 'kurniawati_2025_perceived_usefulness': ['PU1', 'PU2', 'PU3', 'PU4', 'PU5'], 'kurniawati_2025_convenience': ['CON1', 'CON2', 'CON3', 'CON4', 'CON5'], 'kurniawati_2025_behavioral_intention': ['BI1', 'BI2', 'BI3', 'BI4', 'BI5'], 'kurniawati_2025_satisfaction': ['SAT1', 'SAT2', 'SAT3', 'SAT4', 'SAT5'], 'kurniawati_2025_customer_loyalty': ['CL1', 'CL2', 'CL3', 'CL4', 'CL5']}
LO, HI = 1, 5


def load(content):
    return pd.read_excel(io.BytesIO(content)), {}


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
        bad = ~t["resp"].between(LO, HI)
        if bad.any():  # the one BI2 = 6 cell (see header)
            assert name == "kurniawati_2025_behavioral_intention" and bad.sum() == 1, (name, t[bad])
            t = t[~bad]
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
