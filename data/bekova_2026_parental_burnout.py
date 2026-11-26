#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.35117629.v1
# DOI: 10.6084/m9.figshare.35117629.v1 (data)
#   Bekova Z (2026). Emotional Burnout among Parents [Data set]. figshare. https://doi.org/10.6084/m9.figshare.35117629.v1
# License: CC BY 4.0 (record metadata)
# Data: data.xlsx, 120 parents of children with autism in an intervention (E) vs control (C) design. Items live on the MBI_T0/T1/T2 (22
#   items, 0-6) and PSS_T0/T1/T2 (10 items, 0-4) sheets; the Participants sheet holds demographics and scale scores (not carried).
#   The authors' validity flags (attention check, missingness, straight-lining) are carried, not used to filter.
# Covariates: group, parent sex and age, partnered, child ASD support level and age, education, validity flags.
# PII: none.
# Item text: codes only (Russian-language administration).
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
URL = 'https://ndownloader.figshare.com/files/71877538'
N_ROWS = 360
ID_COL = 'ID'
COVS = {'Group': 'cov_group',
 'Parent’s sex (M/F)': 'cov_parent_sex',
 'Parent’s age': 'cov_parent_age',
 'Partner status (1/0)': 'cov_partnered',
 'ASD support level (1/2/3)': 'cov_child_asd_support_level',
 'Child’s age': 'cov_child_age',
 'Education': 'cov_education',
 'valid_mbi': 'cov_valid_mbi',
 'valid_pss': 'cov_valid_pss'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'bekova_2026_mbi': ['mbi_1',
                     'mbi_2',
                     'mbi_3',
                     'mbi_4',
                     'mbi_5',
                     'mbi_6',
                     'mbi_7',
                     'mbi_8',
                     'mbi_9',
                     'mbi_10',
                     'mbi_11',
                     'mbi_12',
                     'mbi_13',
                     'mbi_14',
                     'mbi_15',
                     'mbi_16',
                     'mbi_17',
                     'mbi_18',
                     'mbi_19',
                     'mbi_20',
                     'mbi_21',
                     'mbi_22'],
 'bekova_2026_pss10': ['pss_1', 'pss_2', 'pss_3', 'pss_4', 'pss_5', 'pss_6', 'pss_7', 'pss_8', 'pss_9', 'pss_10']}
# (lo, hi) response range per table
RANGES = {'bekova_2026_mbi': (0, 6), 'bekova_2026_pss10': (0, 4)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = {'bekova_2026_pss10', 'bekova_2026_mbi'}
WAVE_BASE = 0


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Participants', header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """Participants sheet (d) holds the demographics; MBI_T0-2 and PSS_T0-2 sheets hold the items (columns n1..n22 / n1..n10 in Cyrillic).
    Long panel: one row per parent x wave, wave 0/1/2 = T0/T1/T2; the authors' validity flag is carried."""
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    x = pd.read_excel(io.BytesIO(r.content), sheet_name=None)
    demo = d[["ID", "Group", "Parent’s sex (M/F)", "Parent’s age", "Partner status (1/0)", "ASD support level (1/2/3)", "Child’s age", "Education"]]
    rows = []
    for w in (0, 1, 2):
        m = x[f"MBI_T{w}"]; p = x[f"PSS_T{w}"]
        mi = {c: "mbi_" + str(c)[1:] for c in m.columns if str(c).startswith("п")}
        pi = {c: "pss_" + str(c)[1:] for c in p.columns if str(c).startswith("п")}
        a = m[["ID"] + list(mi)].rename(columns=mi).merge(p[["ID"] + list(pi)].rename(columns=pi), on="ID", how="outer")
        a = a.merge(m[["ID", "Valid (1/0)"]].rename(columns={"Valid (1/0)": "valid_mbi"}), on="ID", how="left")
        a = a.merge(p[["ID", "Valid (1/0)"]].rename(columns={"Valid (1/0)": "valid_pss"}), on="ID", how="left")
        a["wave"] = w
        rows.append(a)
    out = pd.concat(rows, ignore_index=True).merge(demo, on="ID", how="left")
    out = out.dropna(subset=["ID"])
    out["Education"] = out["Education"].map(slug)
    return out


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
