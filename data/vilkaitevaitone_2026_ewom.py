#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/Y5S7QY
# DOI: 10.7910/DVN/Y5S7QY (data)
#   Vilkaite-Vaitone N (2026). Replication data for: The Effect of Electronic Word of Mouth: How Credibility Shapes
#   Consumer Purchase Intention [Data set]. Harvard Dataverse. Paper: Revista Brasileira de Gestao de Negocios 28(2).
# License: CC0 1.0 (Dataverse record)
# Data: Supplementary Data 1 - Database.sav, read as format=original (not the .tab conversion): 318 respondents, the
#   deposit's ID column. "Supplementary Data 2 - Variables and codebook.xlsx" gives each construct, item wording and
#   source; the .sav value labels give the anchors 1 = Strongly disagree ... 5 = Totally agree.
# Tables, one per construct, item = the deposit's code: _credibility (EWOMC1-3, eWOM credibility), _argument_strength
#   (AS1-4), _product_attitude (PA1-3), _ewom_adoption (EWOMA1-3), _purchase_intention (PI2-4; the
#   deposit has no PI1), _source_homophily (SH1-4), _source_trust (ST1-3, source trustworthiness).
# Covariates: cov_age_group, cov_gender, cov_education from the .sav value labels.
# PII: none (all columns numeric).
# Item text: held 2026-11-25 (automated_finding/itemtext_hold_2026-11-25.csv) (not built) -- items adapted from the
#   third-party scales the codebook cites; stems in the .sav labels + codebook, anchors in the value labels
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/13664056?format=original'
N_ROWS = 318
ID_COL = 'ID'
COVS = {'AGE': 'cov_age_group', 'GENDER': 'cov_gender', 'EDUCATION': 'cov_education'}
COV_MAPS = {'cov_age_group': {1.0: '20_or_under', 2.0: '21-30', 3.0: '31-40', 4.0: '41-50', 5.0: '50_or_over'},
 'cov_gender': {1.0: 'male', 2.0: 'female'},
 'cov_education': {1.0: 'high_school_or_lower',
                   2.0: 'vocational_diploma',
                   3.0: 'bachelor',
                   4.0: 'postgraduate',
                   5.0: 'other'}}
RENAME = {}
BLOCKS = {'vilkaitevaitone_2026_ewom_credibility': ['EWOMC1', 'EWOMC2', 'EWOMC3'],
 'vilkaitevaitone_2026_argument_strength': ['AS1', 'AS2', 'AS3', 'AS4'],
 'vilkaitevaitone_2026_product_attitude': ['PA1', 'PA2', 'PA3'],
 'vilkaitevaitone_2026_ewom_adoption': ['EWOMA1', 'EWOMA2', 'EWOMA3'],
 'vilkaitevaitone_2026_purchase_intention': ['PI2', 'PI3', 'PI4'],
 'vilkaitevaitone_2026_source_homophily': ['SH1', 'SH2', 'SH3', 'SH4'],
 'vilkaitevaitone_2026_source_trust': ['ST1', 'ST2', 'ST3']}
# (lo, hi) response range per table
RANGES = {'vilkaitevaitone_2026_ewom_credibility': (1, 5),
 'vilkaitevaitone_2026_argument_strength': (1, 5),
 'vilkaitevaitone_2026_product_attitude': (1, 5),
 'vilkaitevaitone_2026_ewom_adoption': (1, 5),
 'vilkaitevaitone_2026_purchase_intention': (1, 5),
 'vilkaitevaitone_2026_source_homophily': (1, 5),
 'vilkaitevaitone_2026_source_trust': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    import tempfile, pyreadstat
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(content)
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    return d


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
