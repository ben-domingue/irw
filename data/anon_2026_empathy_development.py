#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.35055184.v1
# DOI: 10.6084/m9.figshare.35055184.v1 (data)
#   Anonymized authors (2026). Biological and Contextual Correlates of Empathy Development During Emerging Adulthood: Within-Person Fluctuations and Continuity in Individual Differences [Data set]. figshare. https://doi.org/10.6084/m9.figshare.35055184.v1
# License: CC BY 4.0 (record metadata)
# Data: Study1.xlsx (1,995 emerging adults: IRI_1-28 on 0-4 + serotonergic genotypes) and Study2.xlsx (567 college students:
#   W1-W3 x IRI-1..28 and SACQ_1..36 on 1-5 + genotypes). Depositors anonymised on the record, so the table names use
#   'anon'. The same 28 IRI items in both studies -> one table with cov_study and wave.
# Not carried: the SNP / VNTR genotype columns (genetic data; not item responses, and not needed for the tables).
# Blank-string cells in Study2.xlsx are read as missing.
# Covariates: gender, study. PII: none.
# Item text: codes only; IRI (Davis 1983) and SACQ published wording.
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
URL = 'https://ndownloader.figshare.com/files/71620483'
N_ROWS = 3696
ID_COL = 'pid'
COVS = {'Gender': 'cov_gender', 'study': 'cov_study'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'anon_2026_empathy_iri': ['IRI_1',
                           'IRI_2',
                           'IRI_3',
                           'IRI_4',
                           'IRI_5',
                           'IRI_6',
                           'IRI_7',
                           'IRI_8',
                           'IRI_9',
                           'IRI_10',
                           'IRI_11',
                           'IRI_12',
                           'IRI_13',
                           'IRI_14',
                           'IRI_15',
                           'IRI_16',
                           'IRI_17',
                           'IRI_18',
                           'IRI_19',
                           'IRI_20',
                           'IRI_21',
                           'IRI_22',
                           'IRI_23',
                           'IRI_24',
                           'IRI_25',
                           'IRI_26',
                           'IRI_27',
                           'IRI_28'],
 'anon_2026_empathy_sacq': ['SACQ_1',
                            'SACQ_2',
                            'SACQ_3',
                            'SACQ_4',
                            'SACQ_5',
                            'SACQ_6',
                            'SACQ_7',
                            'SACQ_8',
                            'SACQ_9',
                            'SACQ_10',
                            'SACQ_11',
                            'SACQ_12',
                            'SACQ_13',
                            'SACQ_14',
                            'SACQ_15',
                            'SACQ_16',
                            'SACQ_17',
                            'SACQ_18',
                            'SACQ_19',
                            'SACQ_20',
                            'SACQ_21',
                            'SACQ_22',
                            'SACQ_23',
                            'SACQ_24',
                            'SACQ_25',
                            'SACQ_26',
                            'SACQ_27',
                            'SACQ_28',
                            'SACQ_29',
                            'SACQ_30',
                            'SACQ_31',
                            'SACQ_32',
                            'SACQ_33',
                            'SACQ_34',
                            'SACQ_35',
                            'SACQ_36']}
# (lo, hi) response range per table
RANGES = {'anon_2026_empathy_iri': (0, 4), 'anon_2026_empathy_sacq': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = {'anon_2026_empathy_sacq', 'anon_2026_empathy_iri'}
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """Study 1 (this URL): one row per student. Study 2: W1/W2/W3 columns -> one row per student x wave.
    ids are s1_<row> and s2_<row>; Study 1 rows are wave 1. Genotype columns are not carried."""
    geno = ['rs6295', 'rs6311', 'rs6313', 'rs4570625', 'rs7305115', '5HTTVNTR', '5-HTTLPR', '5HTTLPR', 'rs25531']
    d = d.drop(columns=[c for c in d.columns if c in geno])
    d["pid"] = ["s1_%d" % i for i in range(1, len(d) + 1)]
    d["study"] = 1
    d["wave"] = 1
    r = requests.get('https://ndownloader.figshare.com/files/71620486', timeout=600, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    s2 = pd.read_excel(io.BytesIO(r.content))
    s2.columns = [str(c).strip() for c in s2.columns]
    s2 = s2.drop(columns=[c for c in s2.columns if c in geno])
    s2["pid"] = ["s2_%d" % i for i in range(1, len(s2) + 1)]
    parts = []
    for w in (1, 2, 3):
        cols = {c: c[3:].replace("IRI-", "IRI_") for c in s2.columns if c.startswith("W%d_" % w)}
        p = s2[["pid", "Gender"] + list(cols)].rename(columns=cols)
        p["study"] = 2
        p["wave"] = w
        parts.append(p)
    out = pd.concat([d] + parts, ignore_index=True)
    return out.replace(r"^\s*$", np.nan, regex=True)  # blank-string cells in Study 2 are missing


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
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
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
