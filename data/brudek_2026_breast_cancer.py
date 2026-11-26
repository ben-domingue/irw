#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.34961983.v1
# DOI: 10.6084/m9.figshare.34961983.v1 (data)
#   Brudek P (2026). Self-Esteem and Death Anxiety Among Older Women with Breast Cancer: The Mediating Role of Forgiveness and the Moderating Role of Religiosity [Data set]. figshare. https://doi.org/10.6084/m9.figshare.34961983.v1
# License: CC BY 4.0 (record metadata)
# Data: Breast_Cancer_PsychoOncology_Dataset.sav (no value labels), 375 Polish women aged 60-80 with breast cancer; id = row
#   order. Instruments read from the codes and the record (self-esteem, forgiveness, death anxiety, religiosity): ses_1-10
#   Rosenberg (1-4), hfs1-18 Heartland (1-7), seven dap items (1-7; dap_lps is their sum), rsz_01-20 (1-7, two subscales).
# Dropped: the *r reverse-coded copies, all sums/means, stage and treatment dummies.
# Covariates: age, education, marital status, place of residence, szr (code not documented), treatment, cancer stage, illness duration (codes as stored).
# PII: none.
# Item text: no labels; published Polish versions of RSES, HFS, DAP-R and the RSZ.
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
URL = 'https://ndownloader.figshare.com/files/71270194'
N_ROWS = 375
ID_COL = None
COVS = {'wiek': 'cov_age',
 'wykszta': 'cov_education',
 'stancywi': 'cov_marital',
 'miejscez': 'cov_residence',
 'szr': 'cov_szr',
 'rodzajle': 'cov_treatment',
 'stadiumr': 'cov_cancer_stage',
 'cztch': 'cov_illness_duration'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'brudek_2026_rses': ['ses_1', 'ses_2', 'ses_3', 'ses_4', 'ses_5', 'ses_6', 'ses_7', 'ses_8', 'ses_9', 'ses_10'],
 'brudek_2026_hfs': ['hfs1',
                     'hfs2',
                     'hfs3',
                     'hfs4',
                     'hfs5',
                     'hfs6',
                     'hfs7',
                     'hfs8',
                     'hfs9',
                     'hfs10',
                     'hfs11',
                     'hfs12',
                     'hfs13',
                     'hfs14',
                     'hfs15',
                     'hfs16',
                     'hfs17',
                     'hfs18'],
 'brudek_2026_dap': ['dap1', 'dap2', 'dap7', 'dap18', 'dap20', 'dap21', 'dap32'],
 'brudek_2026_religious_meaning': ['rsz_01',
                                   'rsz_02',
                                   'rsz_03',
                                   'rsz_04',
                                   'rsz_05',
                                   'rsz_06',
                                   'rsz_07',
                                   'rsz_08',
                                   'rsz_09',
                                   'rsz_10',
                                   'rsz_11',
                                   'rsz_12',
                                   'rsz_13',
                                   'rsz_14',
                                   'rsz_15',
                                   'rsz_16',
                                   'rsz_17',
                                   'rsz_18',
                                   'rsz_19',
                                   'rsz_20']}
# (lo, hi) response range per table
RANGES = {'brudek_2026_rses': (1, 4),
 'brudek_2026_hfs': (1, 7),
 'brudek_2026_dap': (1, 7),
 'brudek_2026_religious_meaning': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'dap_lps': 'reverse-coded copy, subscale/total score or dummy',
 'hfs2r': 'reverse-coded copy, subscale/total score or dummy',
 'hfs4r': 'reverse-coded copy, subscale/total score or dummy',
 'hfs6r': 'reverse-coded copy, subscale/total score or dummy',
 'hfs7r': 'reverse-coded copy, subscale/total score or dummy',
 'hfs9r': 'reverse-coded copy, subscale/total score or dummy',
 'hfs11r': 'reverse-coded copy, subscale/total score or dummy',
 'hfs13r': 'reverse-coded copy, subscale/total score or dummy',
 'hfs15r': 'reverse-coded copy, subscale/total score or dummy',
 'hfs17r': 'reverse-coded copy, subscale/total score or dummy',
 'f_self': 'reverse-coded copy, subscale/total score or dummy',
 'f_other': 'reverse-coded copy, subscale/total score or dummy',
 'f_syt': 'reverse-coded copy, subscale/total score or dummy',
 'f_wo': 'reverse-coded copy, subscale/total score or dummy',
 'ses_1r': 'reverse-coded copy, subscale/total score or dummy',
 'ses_2r': 'reverse-coded copy, subscale/total score or dummy',
 'ses_4r': 'reverse-coded copy, subscale/total score or dummy',
 'ses_6r': 'reverse-coded copy, subscale/total score or dummy',
 'ses_7r': 'reverse-coded copy, subscale/total score or dummy',
 'ses_wo': 'reverse-coded copy, subscale/total score or dummy',
 'rsz_ori': 'reverse-coded copy, subscale/total score or dummy',
 'rsz_sens': 'reverse-coded copy, subscale/total score or dummy',
 'rsz_tot': 'reverse-coded copy, subscale/total score or dummy',
 'stad_ii': 'reverse-coded copy, subscale/total score or dummy',
 'stad_iii': 'reverse-coded copy, subscale/total score or dummy',
 'stad_iv': 'reverse-coded copy, subscale/total score or dummy',
 'l_horm': 'reverse-coded copy, subscale/total score or dummy',
 'l_cel': 'reverse-coded copy, subscale/total score or dummy',
 'SES_M': 'reverse-coded copy, subscale/total score or dummy',
 'RSZ_M': 'reverse-coded copy, subscale/total score or dummy',
 'F_M': 'reverse-coded copy, subscale/total score or dummy',
 'LPS_M': 'reverse-coded copy, subscale/total score or dummy'}
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
