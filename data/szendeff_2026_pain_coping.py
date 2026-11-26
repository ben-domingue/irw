#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.34901457.v1
# DOI: 10.6084/m9.figshare.34901457.v1 (data)
#   Szendeff C (2026). Dataset for the manuscript entitled "Psychometric evaluation of the Hungarian version of the Pain Coping Inventory in patients with chronic pain" [Data set]. figshare. https://doi.org/10.6084/m9.figshare.34901457.v1
# License: CC BY 4.0 (record metadata)
# Data: one sheet (Munka2), 158 Hungarian adults with chronic pain, the file's Number. PCI 1-34 (34a/34b) on 1-4 with '-' for
#   missing (60 cells), PCS 0-4, HADS 0-3 (as stored), WOC-16 0-3.
# Covariates: gender, age, years of education, employment, work type, marital status, children, pain type/intensity/duration, medication effect (codes).
# PII: none.
# Item text: codes only; published instruments (Hungarian versions).
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
URL = 'https://ndownloader.figshare.com/files/71042415'
N_ROWS = 158
ID_COL = 'Number'
COVS = {'Gender': 'cov_gender',
 'Age': 'cov_age',
 'Oktatásban töltött évek száma': 'cov_years_education',
 'Employment status': 'cov_employment',
 'Type of work': 'cov_work_type',
 'Marital status': 'cov_marital',
 'Children': 'cov_children',
 'Type of chronic pain': 'cov_pain_type',
 'Intensity of pain': 'cov_pain_intensity',
 'Duration of pain': 'cov_pain_duration',
 'Effectiveness of pain medication': 'cov_medication_effect'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'szendeff_2026_pci': ['PCI 1.',
                       'PCI 2.',
                       'PCI 3.',
                       'PCI 4.',
                       'PCI 5.',
                       'PCI 6.',
                       'PCI 7.',
                       'PCI 8.',
                       'PCI 9.',
                       'PCI 10.',
                       'PCI 11.',
                       'PCI 12.',
                       'PCI 13.',
                       'PCI 14.',
                       'PCI 15.',
                       'PCI 16.',
                       'PCI 17.',
                       'PCI 18.',
                       'PCI 19.',
                       'PCI 20.',
                       'PCI 21.',
                       'PCI 22.',
                       'PCI 23.',
                       'PCI 24.',
                       'PCI 25.',
                       'PCI 26.',
                       'PCI 27.',
                       'PCI 28.',
                       'PCI 29.',
                       'PCI 30.',
                       'PCI 31.',
                       'PCI 32.',
                       'PCI 33.',
                       'PCI 34.a',
                       'PCI 34.b'],
 'szendeff_2026_pcs': ['PCS 1.',
                       'PCS 2.',
                       'PCS 3.',
                       'PCS 4.',
                       'PCS 5.',
                       'PCS 6.',
                       'PCS 7.',
                       'PCS 8.',
                       'PCS 9.',
                       'PCS 10.',
                       'PCS 11.',
                       'PCS 12.',
                       'PCS 13.'],
 'szendeff_2026_hads': ['HADS 1.',
                        'HADS 2.',
                        'HADS 3.',
                        'HADS 4.',
                        'HADS 5.',
                        'HADS 6.',
                        'HADS 7.',
                        'HADS 8.',
                        'HADS 9.',
                        'HADS 10.',
                        'HADS 11.',
                        'HADS 12.',
                        'HADS 13.',
                        'HADS 14.'],
 'szendeff_2026_woc16': ['WOC 1.',
                         'WOC 2.',
                         'WOC 3.',
                         'WOC 4.',
                         'WOC 5.',
                         'WOC 6.',
                         'WOC 7.',
                         'WOC 8.',
                         'WOC 9.',
                         'WOC 10.',
                         'WOC 11.',
                         'WOC 12.',
                         'WOC 13.',
                         'WOC 14.',
                         'WOC 15.',
                         'WOC 16.']}
# (lo, hi) response range per table
RANGES = {'szendeff_2026_pci': (1, 4),
 'szendeff_2026_pcs': (0, 4),
 'szendeff_2026_hads': (0, 3),
 'szendeff_2026_woc16': (0, 3)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    for c in ['PCI 1.', 'PCI 2.', 'PCI 3.', 'PCI 4.', 'PCI 5.', 'PCI 6.', 'PCI 7.', 'PCI 8.', 'PCI 9.', 'PCI 10.', 'PCI 11.', 'PCI 12.', 'PCI 13.', 'PCI 14.', 'PCI 15.', 'PCI 16.', 'PCI 17.', 'PCI 18.', 'PCI 19.', 'PCI 20.', 'PCI 21.', 'PCI 22.', 'PCI 23.', 'PCI 24.', 'PCI 25.', 'PCI 26.', 'PCI 27.', 'PCI 28.', 'PCI 29.', 'PCI 30.', 'PCI 31.', 'PCI 32.', 'PCI 33.', 'PCI 34.a', 'PCI 34.b']:
        d[c] = pd.to_numeric(d[c].replace("-", np.nan), errors="coerce")
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
