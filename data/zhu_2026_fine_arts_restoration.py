#!/usr/bin/env python3
# Source: https://doi.org/10.1371/journal.pone.0362667.s001
# DOI: 10.1371/journal.pone.0362667.s001 (data); paper 10.1371/journal.pone.0362667
#   Zhu X, Zhang J, Zhao Y (2026). Anonymized item-level dataset (386 cases) [Data set]. figshare. https://doi.org/10.1371/journal.pone.0362667.s001
# License: CC BY 4.0 (record metadata)
# Data: S1 Dataset xlsx, sheet Data: 386 retained cases x 21 items over six constructs (record description), the
#   file's Case_ID. Every item observed within 1-5.
# Tables: one per construct (the four perceived-restorativeness components are kept separate).
# Covariates: none in the file. PII: none.
# Item text: codes only in the data; wording in the paper (PLOS ONE, pone.0362667).
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
URL = 'https://ndownloader.figshare.com/files/71708494'
N_ROWS = 386
ID_COL = 'Case_ID'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'zhu_2026_being_away': ['BeingAway1', 'BeingAway2', 'BeingAway3', 'BeingAway4'],
 'zhu_2026_compatibility': ['Compatibility1', 'Compatibility2', 'Compatibility3', 'Compatibility4'],
 'zhu_2026_extent': ['Extent1', 'Extent2', 'Extent3'],
 'zhu_2026_fascination': ['Fascination1', 'Fascination2', 'Fascination3', 'Fascination4'],
 'zhu_2026_fine_arts_involvement': ['FineArtsInvolvement1',
                                    'FineArtsInvolvement2',
                                    'FineArtsInvolvement3',
                                    'FineArtsInvolvement4'],
 'zhu_2026_academic_self_efficacy': ['AcademicSelfEfficacy1', 'AcademicSelfEfficacy2', 'AcademicSelfEfficacy3']}
# (lo, hi) response range per table
RANGES = {'zhu_2026_being_away': (1, 5),
 'zhu_2026_compatibility': (1, 5),
 'zhu_2026_extent': (1, 5),
 'zhu_2026_fascination': (1, 5),
 'zhu_2026_fine_arts_involvement': (1, 5),
 'zhu_2026_academic_self_efficacy': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Data', header=0)


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
