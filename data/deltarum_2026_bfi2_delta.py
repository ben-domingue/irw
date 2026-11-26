#!/usr/bin/env python3
# Source: https://zenodo.org/records/24531118
# DOI: 10.5281/zenodo.24531118 (data)
#   Anonymised authors (2026). Beyond the Big Five: Disintegration as a Predictor of Daily Rumination, Anxiety, and Depression [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24531118
# License: CC BY 4.0 (record metadata)
# Data: data.delt.rum.csv, 916 daily questionnaires from 156 Croatian young adults (age 19-25). BFI-2 (60) and DELTA
#   (20) are trait measures, identical on every row of a participant; measures_eng/cro .docx give the instruments.
# Tables: BFI-2 and DELTA, one row per participant. id = order of first appearance (the self-generated code SIFRA_FINAL is not carried).
# Not shipped: the daily PHQ-2, GAD-2 and rumination items (2, 2 and 3 items) -- the file has no day index.
# Covariates: age, gender (code 1-3 as in the file).
# PII: none beyond the self-generated code, which is dropped.
# Item text: measures_eng.delta.rum.docx / measures_cro.delta.rum.docx in the deposit (BFI-2 is a third-party instrument; register check needed).
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
URL = 'https://zenodo.org/api/records/24531118/files/data.delt.rum.csv/content'
N_ROWS = 156
ID_COL = 'pid'
COVS = {'age': 'cov_age', 'gen': 'cov_gender'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'deltarum_2026_bfi2': ['bfi1',
                        'bfi2',
                        'bfi3',
                        'bfi4',
                        'bfi5',
                        'bfi6',
                        'bfi7',
                        'bfi8',
                        'bfi9',
                        'bfi10',
                        'bfi11',
                        'bfi12',
                        'bfi13',
                        'bfi14',
                        'bfi15',
                        'bfi16',
                        'bfi17',
                        'bfi18',
                        'bfi19',
                        'bfi20',
                        'bfi21',
                        'bfi22',
                        'bfi23',
                        'bfi24',
                        'bfi25',
                        'bfi26',
                        'bfi27',
                        'bfi28',
                        'bfi29',
                        'bfi30',
                        'bfi31',
                        'bfi32',
                        'bfi33',
                        'bfi34',
                        'bfi35',
                        'bfi36',
                        'bfi37',
                        'bfi38',
                        'bfi39',
                        'bfi40',
                        'bfi41',
                        'bfi42',
                        'bfi43',
                        'bfi44',
                        'bfi45',
                        'bfi46',
                        'bfi47',
                        'bfi48',
                        'bfi49',
                        'bfi50',
                        'bfi51',
                        'bfi52',
                        'bfi53',
                        'bfi54',
                        'bfi55',
                        'bfi56',
                        'bfi57',
                        'bfi58',
                        'bfi59',
                        'bfi60'],
 'deltarum_2026_delta': ['delta1',
                         'delta2',
                         'delta3',
                         'delta4',
                         'delta5',
                         'delta6',
                         'delta7',
                         'delta8',
                         'delta9',
                         'delta10',
                         'delta11',
                         'delta12',
                         'delta13',
                         'delta14',
                         'delta15',
                         'delta16',
                         'delta17',
                         'delta18',
                         'delta19',
                         'delta20']}
# (lo, hi) response range per table
RANGES = {'deltarum_2026_bfi2': (1, 5), 'deltarum_2026_delta': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'row': 'row number',
 'SIFRA_FINAL': 'self-generated participant code (replaced by pid)',
 'completed_questionnaires': 'number of daily questionnaires the participant completed',
 'dphq1': 'daily diary item; no day index in the file, so not shipped',
 'dphq2': 'daily diary item; no day index in the file, so not shipped',
 'dgad1': 'daily diary item; no day index in the file, so not shipped',
 'dgad2': 'daily diary item; no day index in the file, so not shipped',
 'drum1': 'daily diary item; no day index in the file, so not shipped',
 'drum2': 'daily diary item; no day index in the file, so not shipped',
 'drum3': 'daily diary item; no day index in the file, so not shipped'}


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{})


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """the file is one row per completed daily questionnaire; the trait measures repeat unchanged on every row of a
    participant, so keep one row per participant (first in file order). Participant = SIFRA_FINAL, a self-generated
    code, replaced by its order of first appearance."""
    d = d.rename(columns={d.columns[0]: "row"})
    trait = [c for c in d.columns if c.startswith(("bfi", "delta"))] + ["age", "gen"]
    assert (d.groupby("SIFRA_FINAL", sort=False)[trait].nunique() <= 1).all().all()
    d = d.drop_duplicates("SIFRA_FINAL").reset_index(drop=True)
    d["pid"] = range(1, len(d) + 1)
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
