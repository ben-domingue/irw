#!/usr/bin/env python3
# Source: https://zenodo.org/records/23455377
# DOI: 10.5281/zenodo.23455377 (data)
#   Herrera Lopez LE, Mires Jara AE, Puican Rodriguez VH (2026). Financial literacy and tax management among
#   market traders in northern Peru: underlying data [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata; LEEME.txt)
# Data: datos_anonimizados_educacion_financiera_gestion_tributaria.csv, 218 traders, the deposit's own id.
#   diccionario_de_datos.csv gives every item's dimension, wording and the scale: 1 = nunca .. 5 = siempre.
# Tables: the two instruments as the dictionary groups them (financial literacy = GFN/CFD/TDF, tax management =
#   CTD/OCT/PTE, 12 items each) and the three 4-item moderators (DC, FE, TRD), item = the deposit's code.
# Covariates: none in the deposit (emails and timestamps removed by the depositors).
# PII: none (all columns numeric).
# Item text: not shipped -- Spanish stems for all 36 items in diccionario_de_datos.csv (cheap later build).
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
URL = 'https://zenodo.org/api/records/23455377/files/datos_anonimizados_educacion_financiera_gestion_tributaria.csv/content'
N_ROWS = 218
ID_COL = 'id'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'herrera_2026_financial_literacy': ['GFN1',
                                     'GFN2',
                                     'GFN3',
                                     'GFN4',
                                     'CFD1',
                                     'CFD2',
                                     'CFD3',
                                     'CFD4',
                                     'TDF1',
                                     'TDF2',
                                     'TDF3',
                                     'TDF4'],
 'herrera_2026_tax_management': ['CTD1',
                                 'CTD2',
                                 'CTD3',
                                 'CTD4',
                                 'OCT1',
                                 'OCT2',
                                 'OCT3',
                                 'OCT4',
                                 'PTE1',
                                 'PTE2',
                                 'PTE3',
                                 'PTE4'],
 'herrera_2026_accounting_digitalization': ['DC1', 'DC2', 'DC3', 'DC4'],
 'herrera_2026_business_formalization': ['FE1', 'FE2', 'FE3', 'FE4'],
 'herrera_2026_digital_finance_transform': ['TRD1', 'TRD2', 'TRD3', 'TRD4']}
# (lo, hi) response range per table
RANGES = {'herrera_2026_financial_literacy': (1, 5),
 'herrera_2026_tax_management': (1, 5),
 'herrera_2026_accounting_digitalization': (1, 5),
 'herrera_2026_business_formalization': (1, 5),
 'herrera_2026_digital_finance_transform': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{})


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
