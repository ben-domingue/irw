#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.33623410.v1
# DOI: 10.6084/m9.figshare.33623410.v1 (data)
#   Wren A, Lewis RK, Henely K, Island J (2026). Childhood Trauma and Help-seeking data [Data set]. figshare. https://doi.org/10.6084/m9.figshare.33623410.v1
# License: CC BY 4.0 (record metadata)
# Data: Qualtrics .sav (variable + value labels), 421 rows; the 400 who consented (Q1 = 1) are kept; id = row order. Item
#   identities from the variable labels: Q4-13 ACE, Q14_1-Q19_3 CTQ-SF, Q20/Q22/Q24 GHSQ for three problems, Q26-29 CAGE-AID.
# ACE and CAGE-AID recoded 1/2 -> 1/0 (yes/no).
# Covariates: age, gender, race/ethnicity, education, first-generation, sexual orientation,
#   employment, military service, substance-use timing (codes; labels in the .sav).
# Dropped: consent/eligibility screens, all free-text fields, substance checklists and per-substance 30-day frequencies.
# PII: none.
# Item text: shipped 2026-11-25c for ACE (.sav labels; register ACE = ship); CTQ-SF, GHSQ x3, CAGE-AID held 2026-11-25
#   (automated_finding/itemtext_hold_2026-11-25.csv);
#   automated_finding/itemtext_verification/make_itemtext_repos_2026-11-25c.py
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
URL = 'https://ndownloader.figshare.com/files/68459530'
N_ROWS = 400
ID_COL = None
COVS = {'Q37': 'cov_age',
 'Q38': 'cov_gender',
 'Q39': 'cov_race_ethnicity',
 'Q40': 'cov_education',
 'Q41': 'cov_first_gen',
 'Q42': 'cov_sexual_orientation',
 'Q43': 'cov_employment',
 'Q44': 'cov_military',
 'Q36': 'cov_last_substance_use',
 'Q34': 'cov_still_using',
 'Q31': 'cov_age_first_exposed',
 'Q32': 'cov_age_first_tried'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'wren_2026_ace': ['Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12', 'Q13'],
 'wren_2026_ctq_sf': ['Q14_1',
                      'Q14_2',
                      'Q14_3',
                      'Q14_4',
                      'Q14_5',
                      'Q15_1',
                      'Q15_2',
                      'Q15_3',
                      'Q15_4',
                      'Q15_5',
                      'Q16_1',
                      'Q16_2',
                      'Q16_3',
                      'Q16_4',
                      'Q16_5',
                      'Q17_1',
                      'Q17_2',
                      'Q17_3',
                      'Q17_4',
                      'Q17_5',
                      'Q18_1',
                      'Q18_2',
                      'Q18_3',
                      'Q18_4',
                      'Q18_5',
                      'Q19_1',
                      'Q19_2',
                      'Q19_3'],
 'wren_2026_ghsq_emotional': ['Q20_1',
                              'Q20_2',
                              'Q20_3',
                              'Q20_4',
                              'Q20_5',
                              'Q20_6',
                              'Q20_7',
                              'Q20_8',
                              'Q20_9',
                              'Q20_10'],
 'wren_2026_ghsq_suicidal': ['Q22_1',
                             'Q22_2',
                             'Q22_3',
                             'Q22_4',
                             'Q22_5',
                             'Q22_6',
                             'Q22_7',
                             'Q22_8',
                             'Q22_9',
                             'Q22_10'],
 'wren_2026_ghsq_substance': ['Q24_1',
                              'Q24_2',
                              'Q24_3',
                              'Q24_4',
                              'Q24_5',
                              'Q24_6',
                              'Q24_7',
                              'Q24_8',
                              'Q24_9',
                              'Q24_10'],
 'wren_2026_cage_aid': ['Q26', 'Q27', 'Q28', 'Q29']}
# (lo, hi) response range per table
RANGES = {'wren_2026_ace': (0, 1),
 'wren_2026_ctq_sf': (1, 5),
 'wren_2026_ghsq_emotional': (1, 7),
 'wren_2026_ghsq_suicidal': (1, 7),
 'wren_2026_ghsq_substance': (1, 7),
 'wren_2026_cage_aid': (0, 1)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Q1': 'consent / eligibility screen',
 'Q2': 'consent / eligibility screen',
 'Q3': 'consent / eligibility screen',
 'Q21': 'free text',
 'Q23': 'free text',
 'Q25': 'free text',
 'Q30_1': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q30_2': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q30_3': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q30_4': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q30_5': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q30_6': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q30_7': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q30_8': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q30_9': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_1': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_2': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_3': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_4': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_5': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_6': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_7': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_8': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_9': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_10': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_11': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_12': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q33_10_TEXT': 'free text',
 'Q34_1_TEXT': 'free text',
 'Q35_1': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_2': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_3': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_4': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_5': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_6': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_7': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_8': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_9': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_10': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_11': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_12': 'substance checklist or per-substance 30-day frequency (single questions)',
 'Q35_10_TEXT': 'free text',
 'Q38_5_TEXT': 'free text',
 'Q39_8_TEXT': 'free text',
 'Q42_4_TEXT': 'free text'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    import pyreadstat, tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(content); f.flush()
        d, _ = pyreadstat.read_sav(f.name, user_missing=False)
    return d


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d = d[(d["Q1"] == 1)].reset_index(drop=True)
    for c in ['Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q26', 'Q27', 'Q28', 'Q29']:
        d[c] = d[c].map({1: 1, 2: 0})
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
