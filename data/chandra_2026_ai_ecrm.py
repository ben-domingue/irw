#!/usr/bin/env python3
# Source: https://zenodo.org/records/20897243
# DOI: 10.5281/zenodo.20897243 (data)
#   Chandra H (2026). AI Interactivity in e-CRM and Customer Adoption Resilience in Digital Banking: The Roles of
#   Cognitive Trust, Affective Trust, and Switch-Point Optimization Efficacy [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: "Quesioner Dataset.csv" (semicolon-separated), 400 digital-banking customers, 20 items, every one observed
#   within 1-5. The deposit's "Statistical Analysis Output" workbook names each indicator's construct: AI
#   interactivity (AIC), cognitive trust (COG), affective trust (AFF), switch-point optimisation efficacy (SPO),
#   adoption resilience (ARC). Checked for real structure: mean within-construct r .54-.65 against .27 overall.
#   "Demographic Data.xlsx" is a frequency table only, so no covariates. No respondent id, so id = row order.
# Tables (item = column code): _ai_interactivity, _cognitive_trust, _affective_trust, _switch_point_efficacy,
#   _adoption_resilience.
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
URL = 'https://zenodo.org/api/records/20897243/files/Quesioner%20Dataset.csv/content'
N_ROWS = 400
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'chandra_2026_ai_interactivity': ['AIC1', 'AIC2', 'AIC3', 'AIC4'], 'chandra_2026_cognitive_trust': ['COG1', 'COG2', 'COG3', 'COG4'], 'chandra_2026_affective_trust': ['AFF1', 'AFF2', 'AFF3', 'AFF4'], 'chandra_2026_switch_point_efficacy': ['SPO1', 'SPO2', 'SPO3', 'SPO4'], 'chandra_2026_adoption_resilience': ['ARC1', 'ARC2', 'ARC3', 'ARC4']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_csv(io.BytesIO(content), sep=';')


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
