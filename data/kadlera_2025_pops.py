#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/xc5v2p5pwz
# DOI: 10.17632/xc5v2p5pwz (data)
#   Kadlera A (2025). Development of Perceived Parental Involvement Scale for adolescents [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: "PPI AND POPS DATA SET FOR VALIDITY.sav": 254 Indian adolescents (the confirmatory sample of
#   kadlera_2025_ppis; 242 of its 254 PPIS response patterns recur there, but the "ID" labels were reassigned, so the
#   two tables cannot be linked by id). The validity measure is 42 POPS items (the Perceptions of Parents Scales, by
#   IRW's reading of the code; the deposit carries no labels), stored 1-7. One cell = 67 is outside 1-7 on a single
#   item and is set missing as a data-entry error.
# Table: kadlera_2025_pops, item = the deposit's code (POPS1-POPS42). The file's PPIS columns are not shipped here
#   (they duplicate kadlera_2025_ppis).
# Covariates: as in kadlera_2025_ppis (SPSS value labels); place of residence dropped under the geographic rule.
# PII: none (the one text column holds ID placeholders).
# Item text: not shipped -- no variable labels in the deposit; POPS is a third-party instrument.
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
URL = 'https://data.mendeley.com/public-files/datasets/xc5v2p5pwz/files/a3bcce51-e791-432f-92e1-eef9dd39ded0/file_downloaded'
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
BLOCKS = {'kadlera_2025_pops': ['POPS1',
                       'POPS2',
                       'POPS3',
                       'POPS4',
                       'POPS5',
                       'POPS6',
                       'POPS7',
                       'POPS8',
                       'POPS9',
                       'POPS10',
                       'POPS11',
                       'POPS12',
                       'POPS13',
                       'POPS14',
                       'POPS15',
                       'POPS16',
                       'POPS17',
                       'POPS18',
                       'POPS19',
                       'POPS20',
                       'POPS21',
                       'POPS22',
                       'POPS23',
                       'POPS24',
                       'POPS25',
                       'POPS26',
                       'POPS27',
                       'POPS28',
                       'POPS29',
                       'POPS30',
                       'POPS31',
                       'POPS32',
                       'POPS33',
                       'POPS34',
                       'POPS35',
                       'POPS36',
                       'POPS37',
                       'POPS38',
                       'POPS39',
                       'POPS40',
                       'POPS41',
                       'POPS42']}
# (lo, hi) response range per table
RANGES = {'kadlera_2025_pops': (1, 7)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Placeofresidence': 'geographic (constant), dropped',
 'PPI1': 'duplicates kadlera_2025_ppis',
 'PPI2': 'duplicates kadlera_2025_ppis',
 'PPI3': 'duplicates kadlera_2025_ppis',
 'PPI4': 'duplicates kadlera_2025_ppis',
 'PPI5': 'duplicates kadlera_2025_ppis',
 'PPI6': 'duplicates kadlera_2025_ppis',
 'PPI7': 'duplicates kadlera_2025_ppis',
 'PPI8': 'duplicates kadlera_2025_ppis',
 'PPI9': 'duplicates kadlera_2025_ppis',
 'PPI10': 'duplicates kadlera_2025_ppis',
 'PPI11': 'duplicates kadlera_2025_ppis',
 'PPI12': 'duplicates kadlera_2025_ppis',
 'PPI13': 'duplicates kadlera_2025_ppis',
 'PPI14': 'duplicates kadlera_2025_ppis',
 'PPI15': 'duplicates kadlera_2025_ppis',
 'PPI16': 'duplicates kadlera_2025_ppis',
 'PPI17': 'duplicates kadlera_2025_ppis',
 'PPI18': 'duplicates kadlera_2025_ppis',
 'PPI19': 'duplicates kadlera_2025_ppis',
 'PPI20': 'duplicates kadlera_2025_ppis',
 'PPI21': 'duplicates kadlera_2025_ppis',
 'PPI22': 'duplicates kadlera_2025_ppis',
 'PPI23': 'duplicates kadlera_2025_ppis'}


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
    po = [f"POPS{i}" for i in range(1, 43)]
    bad = d[po] > 7
    assert bad.sum().sum() == 1 and (d[po] == 67).sum().sum() == 1
    d[po] = d[po].mask(bad)
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
