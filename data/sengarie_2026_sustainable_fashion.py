#!/usr/bin/env python3
# Source: https://zenodo.org/records/23879195
# DOI: 10.5281/zenodo.23879195 (data)
#   Sengarie N, Ratnaputri CI (2026). The Role of E-Commerce Information Systems in Supporting Sustainable Fashion Consumption [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23879195
# License: CC BY 4.0 (record metadata)
# Data: sheet 'Anonymized Data', 250 Indonesian consumers aged 17-35, the deposit's Respondent_ID; the 'Codebook'
#   sheet gives each code's construct and English wording. No anchors; every item observed within 1-5.
# Tables: one per codebook construct. Covariates: none in the deposit. PII: none.
# Item text: English stems for all 42 items in the xlsx 'Codebook' sheet (cheap later build).
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/23879195/files/E-Commerce%20Information%20Systems%20in%20Supporting%20Sustainable%20Fashion%20Consumption%20Dataset.xlsx/content'
N_ROWS = 250
ID_COL = 'Respondent_ID'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'sengarie_2026_env_awareness': ['EW1', 'EW2', 'EW3', 'EW4', 'EW5', 'EW6', 'EW7', 'EW8', 'EW9', 'EW10', 'EW11'],
 'sengarie_2026_product_quality': ['PPQ1',
                                   'PPQ2',
                                   'PPQ3',
                                   'PPQ4',
                                   'PPQ5',
                                   'PPQ6',
                                   'PPQ7',
                                   'PPQ8',
                                   'PPQ9',
                                   'PPQ10',
                                   'PPQ11',
                                   'PPQ12',
                                   'PPQ13',
                                   'PPQ14',
                                   'PPQ15'],
 'sengarie_2026_green_brand_image': ['GBI1', 'GBI2', 'GBI3', 'GBI4', 'GBI5', 'GBI6', 'GBI7', 'GBI8', 'GBI9'],
 'sengarie_2026_purchase_intention': ['PI1', 'PI2', 'PI3', 'PI4', 'PI5', 'PI6', 'PI7']}
# (lo, hi) response range per table
RANGES = {'sengarie_2026_env_awareness': (1, 5),
 'sengarie_2026_product_quality': (1, 5),
 'sengarie_2026_green_brand_image': (1, 5),
 'sengarie_2026_purchase_intention': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Anonymized Data', header=1)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert d[ID_COL].is_unique, "duplicate ids"
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        if cov in COV_MAPS:
            d[src] = d[src].map(lambda v: v.strip() if isinstance(v, str) else v)
            d[cov] = d[src].map(COV_MAPS[cov])
            assert d[cov].notna().sum() == d[src].notna().sum(), (cov, set(d[src].dropna()) - set(COV_MAPS[cov]))
        else:
            d[cov] = d[src]
    covs = list(dict.fromkeys(COVS.values()))
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
