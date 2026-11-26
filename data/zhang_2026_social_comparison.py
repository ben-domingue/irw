#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.33439171.v1
# DOI: 10.6084/m9.figshare.33439171.v1 (data)
#   Zhang K (2026). Social Comparison and Self-esteem [Data set]. figshare. https://doi.org/10.6084/m9.figshare.33439171.v1
# License: CC BY 4.0 (record metadata)
# Data: Data2.xlsx (study 1, 155 participants: SC1-4, ES1-3, PB1-4) and Data3.xlsx (study 2, 132: SC1-4, PB1-4, Z1-5),
#   each with a randomised scenario code and a 1-10 social-status rating. The questionnaires are in the deposit's
#   Appendix .doc files; the codes are not expanded in the data, so tables keep the codes.
# Same SC and PB items in both studies -> one table each with cov_study; id = s<study>_<No.>.
# Data1.xlsx (pretest of the scenario materials: two 3-item manipulation checks) is not shipped.
# Dropped from study 1: three contrast-dummy columns re-coding the scenario.
# PII: none.
# Item text: codes only in the data; the questionnaires are in Appendix A-C (.doc) of the deposit.
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
URL = 'https://ndownloader.figshare.com/files/68221906'
N_ROWS = 287
ID_COL = 'pid'
COVS = {'study': 'cov_study', 'scenario': 'cov_scenario', 'Social status': 'cov_subjective_status'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'zhang_2026_sc': ['SC1', 'SC2', 'SC3', 'SC4'],
 'zhang_2026_pb': ['PB1', 'PB2', 'PB3', 'PB4'],
 'zhang_2026_es': ['ES1', 'ES2', 'ES3'],
 'zhang_2026_z': ['Z1', 'Z2', 'Z3', 'Z4', 'Z5']}
# (lo, hi) response range per table
RANGES = {'zhang_2026_sc': (1, 5), 'zhang_2026_pb': (1, 5), 'zhang_2026_es': (1, 5), 'zhang_2026_z': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'No.': 'row number, folded into id', 'Random scenarios': 'carried as cov_scenario'}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """stack study 1 (Data2.xlsx, this URL) and study 2 (Data3.xlsx): same SC and PB items, ids prefixed by study"""
    r = requests.get('https://ndownloader.figshare.com/files/68221909', timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d2 = pd.read_excel(io.BytesIO(r.content))
    d2.columns = [str(c).strip() for c in d2.columns]
    d2 = d2.rename(columns={"social status": "Social status"})
    d = d.drop(columns=["普通与网红", "运动员与普通", "网红与运动员"])
    d["study"] = 1
    d2["study"] = 2
    d = pd.concat([d, d2], ignore_index=True)
    d["pid"] = "s" + d["study"].astype(str) + "_" + d["No."].astype(int).astype(str)
    d["scenario"] = "s" + d["study"].astype(str) + "_" + d["Random scenarios"].astype(int).astype(str)
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
