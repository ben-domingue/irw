#!/usr/bin/env python3
# Source: https://zenodo.org/records/24318294
# DOI: 10.5281/zenodo.24318294 (data)
#   Beege M (2026). Same-language subtitles in instructional video: Conceptual learning, cognitive load, and the role of learner characteristics [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24318294
# License: CC BY 4.0 (record metadata)
# Data: Dataset_Subtitles.xlsx, 172 German secondary pupils (age 13-16, grades 8-9) watching an instructional video with or
#   without subtitles (group), the file's id. Scored tests (PK, LC, learning test L*A/L*B) are 0/1; interest 1-5; cognitive load
#   (ICL/ECL/GCL) 1-9.
# Covariates: condition, gender, age, grade, three standardised reading-test scores (LV, LGN, LGS).
# Dropped: section-marker columns, consent flag, raw reading scores, all overall scores.
# PII: none.
# Item text: codes only in the deposit.
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
URL = 'https://zenodo.org/api/records/24318294/files/Dataset_Subtitles.xlsx/content'
N_ROWS = 172
ID_COL = 'id'
COVS = {'group': 'cov_condition',
 'gender': 'cov_gender',
 'age': 'cov_age',
 'class': 'cov_grade',
 'LV': 'cov_reading_lv_t',
 'LGN': 'cov_reading_lgn_t',
 'LGS': 'cov_reading_lgs_t'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'beege_2026_prior_knowledge': ['PK1', 'PK2', 'PK3', 'PK4', 'PK5', 'PK6', 'PK7', 'PK8', 'PK9', 'PK10'],
 'beege_2026_listening_comprehension': ['LC1', 'LC2', 'LC3S', 'LC4', 'LC5S', 'LC6S', 'LC7', 'LC8'],
 'beege_2026_interest': ['I1', 'I2i', 'I3', 'I4i', 'I5', 'I6i', 'I7', 'I8i'],
 'beege_2026_intrinsic_load': ['ICL1', 'ICL2', 'ICL3', 'ICL4', 'ICL5'],
 'beege_2026_extraneous_load': ['ECL1', 'ECL2', 'ECL3', 'ECL4', 'ECL5'],
 'beege_2026_germane_load': ['GCL1', 'GCL2', 'GCL3', 'GCL4', 'GCL5', 'GCL6', 'GCL7'],
 'beege_2026_learning_test': ['L1A',
                              'L2A',
                              'L3A',
                              'L4A',
                              'L5A',
                              'L6A',
                              'L7A',
                              'L8A',
                              'L9A',
                              'L10A',
                              'L11A',
                              'L12A',
                              'L13A',
                              'L14A',
                              'L15B',
                              'L16B',
                              'L17B',
                              'L18B']}
# (lo, hi) response range per table
RANGES = {'beege_2026_prior_knowledge': (0, 1),
 'beege_2026_listening_comprehension': (0, 1),
 'beege_2026_interest': (1, 5),
 'beege_2026_intrinsic_load': (1, 9),
 'beege_2026_extraneous_load': (1, 9),
 'beege_2026_germane_load': (1, 9),
 'beege_2026_learning_test': (0, 1)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'DSGVO': 'section marker, consent flag, raw reading-test score or overall score',
 'Demographics': 'section marker, consent flag, raw reading-test score or overall score',
 'Prior_Knowledge': 'section marker, consent flag, raw reading-test score or overall score',
 'Listening_Comprehension': 'section marker, consent flag, raw reading-test score or overall score',
 'Reading_Comprehension': 'section marker, consent flag, raw reading-test score or overall score',
 'LV_raw': 'section marker, consent flag, raw reading-test score or overall score',
 'LGN_raw': 'section marker, consent flag, raw reading-test score or overall score',
 'LGS_raw': 'section marker, consent flag, raw reading-test score or overall score',
 'Interest': 'section marker, consent flag, raw reading-test score or overall score',
 'Cognitive_Load': 'section marker, consent flag, raw reading-test score or overall score',
 'Learning_Test': 'section marker, consent flag, raw reading-test score or overall score',
 'Scores': 'section marker, consent flag, raw reading-test score or overall score',
 'PK_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'LC_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'RC_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'I_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'ICL_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'ECL_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'GCL_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'LA_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'LB_overall': 'section marker, consent flag, raw reading-test score or overall score',
 'L_overall': 'section marker, consent flag, raw reading-test score or overall score'}
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
