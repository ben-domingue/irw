#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/xc5v2p5pwz
# DOI: 10.17632/xc5v2p5pwz (data)
#   Kadlera A (2025). Development of Perceived Parental Involvement Scale for adolescents [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: "CFE DATA SET FOR ANALYSIS.sav", the confirmatory sample: 254 Indian adolescents aged 14-17 in Bangalore, the
#   deposit's Name column ("ID1".."ID254", placeholders, not names). 23 draft PPIS items (the record says 14 were
#   retained, on two factors, Parental Engagement and Parental Control; the deposit does not say which 14), stored
#   1-5 with SPSS value labels for the demographics only. One cell, PPI21 = 35, is outside 1-5 on a single item and is
#   set missing as a data-entry error.
#   Not shipped: the EFA sample ("EFA DATA SET FOR ANALYSIS.sav", 246 rows), because rows ID104-ID109 reappear as
#   ID181-ID187 with the same 23 responses (7 copied rows, some with a different age), so its rows cannot be trusted;
#   and the PPIS columns of the validity file, which hold this same sample re-keyed (see kadlera_2025_pops.py).
# Table: kadlera_2025_ppis, all 23 draft items, item = the deposit's code (PPI1-PPI23).
# Covariates: cov_gender, cov_age, cov_class, cov_ses, cov_family_type, cov_siblings, cov_lives_with,
#   cov_close_attachment, cov_more_time_with (SPSS value labels). Place of residence is one value (Bangalore) and is
#   dropped under the geographic rule.
# PII: none (the one text column holds ID placeholders).
# Item text: not shipped -- no variable labels; the wording is in the scale-development paper.
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
URL = 'https://data.mendeley.com/public-files/datasets/xc5v2p5pwz/files/ef56331e-329d-4166-8d8e-53deb7369b9d/file_downloaded'
N_ROWS = 254
ID_COL = 'Name'
COVS = {'Gender': 'cov_gender',
 'Age': 'cov_age',
 'Class': 'cov_class',
 'SES': 'cov_ses',
 'FamilyStatus': 'cov_family_type',
 'Siblingstatus': 'cov_siblings',
 'Parentsstatus': 'cov_lives_with',
 'closeattachment': 'cov_close_attachment',
 'spendsmoretime': 'cov_more_time_with'}
COV_MAPS = {'cov_gender': {1.0: 'female', 2.0: 'male'},
 'cov_ses': {1.0: 'low', 2.0: 'middle', 3.0: 'upper'},
 'cov_family_type': {1.0: 'joint', 2.0: 'nuclear'},
 'cov_siblings': {1.0: 'no', 2.0: 'yes'},
 'cov_lives_with': {1.0: 'both', 2.0: 'father', 3.0: 'mother', 4.0: 'grandparents'},
 'cov_close_attachment': {1.0: 'both', 2.0: 'father', 3.0: 'mother', 4.0: 'none'},
 'cov_more_time_with': {1.0: 'both', 2.0: 'father', 3.0: 'mother', 4.0: 'none'}}
RENAME = {}
BLOCKS = {'kadlera_2025_ppis': ['PPI1',
                       'PPI2',
                       'PPI3',
                       'PPI4',
                       'PPI5',
                       'PPI6',
                       'PPI7',
                       'PPI8',
                       'PPI9',
                       'PPI10',
                       'PPI11',
                       'PPI12',
                       'PPI13',
                       'PPI14',
                       'PPI15',
                       'PPI16',
                       'PPI17',
                       'PPI18',
                       'PPI19',
                       'PPI20',
                       'PPI21',
                       'PPI22',
                       'PPI23']}
# (lo, hi) response range per table
RANGES = {'kadlera_2025_ppis': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Placeofresidence': 'geographic (constant), dropped', 'VAR00001': 'empty column'}


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
    assert (d["PPI21"] == 35).sum() == 1 and ((d[[f"PPI{i}" for i in range(1, 24)]] > 5).sum().sum() == 1)
    d.loc[d["PPI21"] == 35, "PPI21"] = None
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
