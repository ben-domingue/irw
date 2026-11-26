#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/19SPJC
# DOI: 10.7910/DVN/19SPJC (data)
#   Bansal G (2026). Raw data - Ambivalent nature of trust in AI [Data set]. Dataverse. https://doi.org/10.7910/DVN/19SPJC
# License: CC0 1.0 (record metadata)
# Data: 'AI adoption Data N 702.xlsx' (Qualtrics export, 2023), 702 adults; id = row order. No codebook: blocks are read from
#   the item prefixes; Big Five blocks are two 5-item sets per trait (IPIP-style), privacy concern the four CFIP facets + an
#   overall block. Several trust-facet / context codes (TT*, Con_*, Com, OBT, Real) are kept as codes.
# Covariates: age, gender, education, employment (codes).
# Dropped: the constant consent item and empty "other" text fields.
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
URL = 'https://dataverse.harvard.edu/api/access/datafile/14279339'
N_ROWS = 702
ID_COL = None
COVS = {'Age': 'cov_age', 'Gender': 'cov_gender', 'Edn': 'cov_education', 'Emp': 'cov_employment'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'bansal_2026_com': ['Com1', 'Com2', 'Com3', 'Com4', 'Com5'],
 'bansal_2026_ttf': ['TTF1', 'TTF2', 'TTF3', 'TTF4', 'TTF5'],
 'bansal_2026_tth': ['TTH1', 'TTH2', 'TTH3', 'TTH4', 'TTH5'],
 'bansal_2026_ttr': ['TTR1', 'TTR2', 'TTR3', 'TTR4', 'TTR5'],
 'bansal_2026_tti': ['TTI1', 'TTI2', 'TTI3', 'TTI4', 'TTI5'],
 'bansal_2026_ttc': ['TTC1', 'TTC2', 'TTC3', 'TTC4', 'TTC5'],
 'bansal_2026_ttb': ['TTB1', 'TTB2', 'TTB3', 'TTB4', 'TTB5'],
 'bansal_2026_intention': ['Int1', 'Int2', 'Int3', 'Int4', 'Int5'],
 'bansal_2026_obt': ['OBT1', 'OBT2', 'OBT3', 'OBT4', 'OBT5'],
 'bansal_2026_reactance': ['React1', 'React2', 'React3', 'React4', 'React5'],
 'bansal_2026_con_sts': ['Con_Sts1', 'Con_Sts2', 'Con_Sts3'],
 'bansal_2026_con_cpx': ['Con_Cpx1', 'Con_Cpx2', 'Con_Cpx3'],
 'bansal_2026_con_job': ['Con_Job1', 'Con_Job2', 'Con_Job3'],
 'bansal_2026_con_pc': ['Con_PC1', 'Con_PC2', 'Con_PC3'],
 'bansal_2026_agreeableness': ['AGR1_1',
                               'AGR1_2',
                               'AGR1_3',
                               'AGR1_4',
                               'AGR1_5',
                               'AGR2_1',
                               'AGR2_2',
                               'AGR2_3',
                               'AGR2_4',
                               'AGR2_5'],
 'bansal_2026_conscientiousness': ['CON1_1',
                                   'CON1_2',
                                   'CON1_3',
                                   'CON1_4',
                                   'CON1_5',
                                   'CON2_1',
                                   'CON2_2',
                                   'CON2_3',
                                   'CON2_4',
                                   'CON2_5'],
 'bansal_2026_emotional_stability': ['EMN1_1',
                                     'EMN1_2',
                                     'EMN1_3',
                                     'EMN1_4',
                                     'EMN1_5',
                                     'EMN2_1',
                                     'EMN2_2',
                                     'EMN2_3',
                                     'EMN2_4',
                                     'EMN2_5'],
 'bansal_2026_extraversion': ['EXT1_1',
                              'EXT1_2',
                              'EXT1_3',
                              'EXT1_4',
                              'EXT1_5',
                              'EXT2_1',
                              'EXT2_2',
                              'EXT2_3',
                              'EXT2_4',
                              'EXT2_5'],
 'bansal_2026_intellect': ['INTEL1_1',
                           'INTEL1_2',
                           'INTEL1_3',
                           'INTEL1_4',
                           'INTEL1_5',
                           'INTEL2_1',
                           'INTEL2_2',
                           'INTEL2_3',
                           'INTEL2_4',
                           'INTEL2_5'],
 'bansal_2026_pc_collection': ['PCCOL1_1', 'PCCOL1_2', 'PCCOL1_3', 'PCCOL2'],
 'bansal_2026_pc_secondary_use': ['PCSEC1_1', 'PCSEC1_2', 'PCSEC1_3', 'PCSEC2'],
 'bansal_2026_pc_unauthorized_access': ['PCUA1_1', 'PCUA1_2', 'PCUA1_3', 'PCUA2'],
 'bansal_2026_pc_errors': ['PCERR1_1', 'PCERR1_2', 'PCERR1_3', 'PCERR2'],
 'bansal_2026_pc_overall': ['PCOver1',
                            'PCOver2',
                            'PCOver3',
                            'PCOver4',
                            'PCOver5',
                            'PCOver6',
                            'PCOver7',
                            'PCOver8',
                            'PCOver9'],
 'bansal_2026_ai_experience': ['AIExp_1', 'AIExp_2', 'AIExp_3', 'AIExp_4'],
 'bansal_2026_disposition_trust': ['DISP1', 'DISP2', 'DISP3'],
 'bansal_2026_realism': ['Real1', 'Real2', 'Real3'],
 'bansal_2026_marker': ['Marker1', 'Marker2', 'Marker3', 'Marker4']}
# (lo, hi) response range per table
RANGES = {'bansal_2026_com': (1, 7),
 'bansal_2026_ttf': (1, 7),
 'bansal_2026_tth': (1, 7),
 'bansal_2026_ttr': (1, 7),
 'bansal_2026_tti': (1, 7),
 'bansal_2026_ttc': (1, 7),
 'bansal_2026_ttb': (1, 7),
 'bansal_2026_intention': (1, 7),
 'bansal_2026_obt': (1, 7),
 'bansal_2026_reactance': (1, 7),
 'bansal_2026_con_sts': (1, 7),
 'bansal_2026_con_cpx': (1, 7),
 'bansal_2026_con_job': (1, 7),
 'bansal_2026_con_pc': (1, 7),
 'bansal_2026_agreeableness': (1, 7),
 'bansal_2026_conscientiousness': (1, 7),
 'bansal_2026_emotional_stability': (1, 7),
 'bansal_2026_extraversion': (1, 7),
 'bansal_2026_intellect': (1, 7),
 'bansal_2026_pc_collection': (1, 7),
 'bansal_2026_pc_secondary_use': (1, 7),
 'bansal_2026_pc_unauthorized_access': (1, 7),
 'bansal_2026_pc_errors': (1, 7),
 'bansal_2026_pc_overall': (1, 7),
 'bansal_2026_ai_experience': (1, 5),
 'bansal_2026_disposition_trust': (1, 7),
 'bansal_2026_realism': (1, 7),
 'bansal_2026_marker': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Consent2': 'consent (constant)',
 'Gender_3_TEXT': 'empty free-text "other"',
 'Edn_7_TEXT': 'empty free-text "other"',
 'Emp_9_TEXT': 'empty free-text "other"'}
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
