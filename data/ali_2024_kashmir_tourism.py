#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/Z6HW2X
# DOI: 10.7910/DVN/Z6HW2X (data)
#   Ali S (2024). Replication data for Unveiling the Nexus: Exploring the impact of Tourism Service
#   Quality, Cultural Sensitivity and Environmental Sustainability on Tourist Satisfaction and Revisit
#   Intention in the Context of Kashmir [Data set]. Harvard Dataverse.
# License: CC0 1.0 (Dataverse record)
# Data: Data Set 3.sav (Dataverse format=original), 259 tourists in Kashmir; value labels 1 Strongly
#   Disagree .. 5 Strongly Agree.
# Tables (item = column name): TSQ1-3 tourism service quality, CS1-3 cultural sensitivity, ES1-3
#   environmental sustainability, TS1-5 tourist satisfaction, RI1-4 revisit intention. id = row order.
# Covariates (.sav value labels): cov_age_group, cov_gender, cov_education, cov_income.
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/10735670?format=original'
N_ROWS = 259
ID_COL = None
COVS = {'Age': 'cov_age_group', 'Gender': 'cov_gender', 'EducationLevel': 'cov_education', 'AnnualIncome': 'cov_income'}
COV_MAPS = {'cov_age_group': 'SAV', 'cov_gender': 'SAV', 'cov_education': 'SAV', 'cov_income': 'SAV'}
RENAME = {}
BLOCKS = {'ali_2024_tourism_service_quality': ['TSQ1', 'TSQ2', 'TSQ3'], 'ali_2024_cultural_sensitivity': ['CS1', 'CS2', 'CS3'], 'ali_2024_environmental_sustainability': ['ES1', 'ES2', 'ES3'], 'ali_2024_tourist_satisfaction': ['TS1', 'TS2', 'TS3', 'TS4', 'TS5'], 'ali_2024_revisit_intention': ['RI1', 'RI2', 'RI3', 'RI4']}
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
