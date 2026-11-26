#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/Questionnaire_Data_Survey_on_SDFs_/29373668
# DOI: 10.6084/m9.figshare.29373668 (data); paper 10.1371/journal.pone.0324989
#   Li J, Wang X, Gu Q (2025). Shopping festival atmospherics of China's Singles Day shopping festival and
#   participants' perception: Scale development and validation. PLOS ONE. Data: S1 file, figshare.
# License: CC BY 4.0 (figshare record metadata; PLOS ONE)
# Data: pone.0324989.s001.xlsx, sheet "Total sample =686": 686 Chinese Singles Day participants, the deposit's own
#   Number column. The sheets "Sample 1 (n=343) EFA" and "Sample 2 (n=343) CFA" are the same respondents split in two,
#   not extra people, so only the total sheet is read. Q8-Q26 are the 19 candidate atmospherics statements (the paper
#   retains 18 attributes in three dimensions: cultural, social, online cues), observed on 1-7 (seven-point).
# Tables: _sdsf_atmospherics, one table of the 19 statements, item = the deposit's code (Q8-Q26). The paper's three
#   dimensions are not split here because the deposit does not say which statement went where or which was dropped.
# Covariates: none. Q1-Q7 (gender, age, education, occupation, income, participation and chat counts) are named in the
#   "Final Questionnaire Description" sheet but their codes have no key, so they are not carried.
# PII: none (all columns numeric).
# Item text: not shipped -- the description sheet gives every stem, but no anchors, and Q18 and Q23 carry the same
#   wording ("I prepare a long time for the day every year") while their responses differ (identical in 44% of rows),
#   so one of the two stems is wrong in the sheet.
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
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://ndownloader.figshare.com/files/55534382'
N_ROWS = 686
ID_COL = 'Number'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'li_2025_sdsf_atmospherics': ['Q8',
                               'Q9',
                               'Q10',
                               'Q11',
                               'Q12',
                               'Q13',
                               'Q14',
                               'Q15',
                               'Q16',
                               'Q17',
                               'Q18',
                               'Q19',
                               'Q20',
                               'Q21',
                               'Q22',
                               'Q23',
                               'Q24',
                               'Q25',
                               'Q26']}
# (lo, hi) response range per table
RANGES = {'li_2025_sdsf_atmospherics': (1, 7)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Q1': 'unkeyed demographic / usage code',
 'Q2': 'unkeyed demographic / usage code',
 'Q3': 'unkeyed demographic / usage code',
 'Q4': 'unkeyed demographic / usage code',
 'Q5': 'unkeyed demographic / usage code',
 'Q6': 'unkeyed demographic / usage code',
 'Q7': 'unkeyed demographic / usage code'}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0)


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
    assert len(d) == N_ROWS, len(d)
    d = d.rename(columns=RENAME)
    d = prep(d)
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
    covs = list(COVS.values())
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
