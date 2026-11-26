#!/usr/bin/env python3
# Source: https://doi.org/10.1371/journal.pone.0363619.s003
# DOI: 10.1371/journal.pone.0363619.s003 (data); paper 10.1371/journal.pone.0363619
#   Han Q (2026). Full item-level dataset containing the smartphone-use and interaction-anxiety responses (S3 Dataset) [Data set]. figshare. https://doi.org/10.1371/journal.pone.0363619.s003
# License: CC BY 4.0 (record metadata)
# Data: S3 Dataset (pone.0363619.s003.csv), 1,025 Chinese university students, the file's row_id. Item-level smartphone-use
#   (mpa01-22) and raw interaction-anxiety (sa01-15_raw) responses on 1-5, plus the three PARS-3 exercise ratings
#   (PARS1/2/3 = exercise_intensity/duration/frequency_ord).
# The S2 Dataset of the same article (totals only) is not shipped.
# Covariates: sex, grade, major, only child, sedentary band, and the authors' three data-quality flags (kept, not used to filter).
# PII: none.
# Item text: codes only; wording in the paper (PLOS ONE pone.0363619).
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
URL = 'https://ndownloader.figshare.com/files/71796622'
N_ROWS = 1025
ID_COL = 'row_id'
COVS = {'sex': 'cov_sex',
 'grade': 'cov_grade',
 'major_type': 'cov_major',
 'only_child': 'cov_only_child',
 'sedentary_ord': 'cov_sedentary_band',
 'flag_phone_straightline': 'cov_flag_phone_straightline',
 'flag_ias_straightline': 'cov_flag_ias_straightline',
 'flag_identical_response_pattern': 'cov_flag_identical_pattern'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'han_2026_smartphone_use': ['mpa01',
                             'mpa02',
                             'mpa03',
                             'mpa04',
                             'mpa05',
                             'mpa06',
                             'mpa07',
                             'mpa08',
                             'mpa09',
                             'mpa10',
                             'mpa11',
                             'mpa12',
                             'mpa13',
                             'mpa14',
                             'mpa15',
                             'mpa16',
                             'mpa17',
                             'mpa18',
                             'mpa19',
                             'mpa20',
                             'mpa21',
                             'mpa22'],
 'han_2026_interaction_anxiety': ['sa01_raw',
                                  'sa02_raw',
                                  'sa03_raw',
                                  'sa04_raw',
                                  'sa05_raw',
                                  'sa06_raw',
                                  'sa07_raw',
                                  'sa08_raw',
                                  'sa09_raw',
                                  'sa10_raw',
                                  'sa11_raw',
                                  'sa12_raw',
                                  'sa13_raw',
                                  'sa14_raw',
                                  'sa15_raw'],
 'han_2026_pars3': ['PARS1', 'PARS2', 'PARS3']}
# (lo, hi) response range per table
RANGES = {'han_2026_smartphone_use': (1, 5), 'han_2026_interaction_anxiety': (1, 5), 'han_2026_pars3': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'sex_male': 'dummy of sex',
 'grade_num': 'numeric copy of grade',
 'grade_freshman': 'dummy of grade',
 'only_child_yes': 'dummy of only_child',
 'sedentary_label': 'label of sedentary_ord',
 'exercise_index': 'PARS-3 score',
 'exercise_level': 'banded PARS-3 score',
 'phone_total': 'sum score',
 'ias_total_conventional': 'sum score',
 'ias_total_legacy': 'sum score'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{'encoding': 'utf-8-sig'})


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    for c in ["sex", "grade", "major_type", "only_child"]:
        d[c] = d[c].map(slug)
    return d.rename(columns={"exercise_intensity_ord": "PARS1", "exercise_duration_ord": "PARS2", "exercise_frequency_ord": "PARS3"})


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
